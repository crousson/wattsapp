class Site < ActiveRecord::Base

  has_many :meters
  has_many :site_daily_productions
  has_many :meter_readings
  attr_accessible :category, :installed_at, :lat, :lon, :name

  validates_presence_of :name, :installed_at, :category

  def active_meter
    meters.where(:active => true).first
  end

  def change_meter(date=DateTime.now.to_date, offset=0)
    if !(m = active_meter).nil?
      m.disposed_at = date
      m.active = false
      m.save
    end
    Meter.create :site => self,
      :installed_at => date,
      :offset => offset
  end

  def compute_missing_readings

    # total_production = site_daily_productions.sum(:production)
    t1 = nil
    t2 = nil

    meter_readings.where("source in (:source)", { :source => %w(imported manual) })
      .order("date desc")
      .each do |reading|
        t1, t2 = reading, t1
        if !t2.nil?
          interpolate_between t1, t2
        end
    end
    
  end

  def get_production_between(t1, t2)
    site_daily_productions
      .where('date between :d1 and :d2 and date < :d2', { :d1 => t1.date, :d2 => t2.date })
      .sum(:production)
  end

  def index_meter_readings_by_date_between(t1, t2)
    reading_ids = {}
    meter_readings.where('date > :d1 and date < :d2', { :d1 => t1.date, :d2 => t2.date })
      .each do |reading|

        reading_ids[reading.date] = reading.id

    end
    reading_ids
  end

  def interpolate_between(t1, t2)

    index_delta = t2.vindex - t1.vindex
    production = get_production_between t1, t2

    current_vindex = t1.vindex
    current_reading_value = 0
    if t1.meter_id == t2.meter_id
      current_reading_value = t1.value
    else
      current_reading_value = t2.meter.offset
    end

    reading_ids = index_meter_readings_by_date_between t1, t2

    site_daily_productions.where('date > :d1 and date < :d2', { :d1 => t1.date, :d2 => t2.date })
      .order("date")
      .each do |day|

        delta = index_delta * day.production / production
        current_reading_value += delta
        current_vindex += delta

        reading_id = reading_ids[day.date]
        if reading_id.nil?

          MeterReading.create :meter => t2.meter,
            :value => current_reading_value,
            :date => day.date,
            :vindex => current_vindex,
            :source => "computed",
            :site => self

        else

          reading = MeterReading.find(reading_id)
          if reading.source == "computed"
            reading.value = current_reading_value
            reading.vindex = current_vindex
            reading.save
          end

        end

    end

  end

end
