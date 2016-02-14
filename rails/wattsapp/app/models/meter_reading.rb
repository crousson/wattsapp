class MeterReading < ActiveRecord::Base
  belongs_to :meter
  belongs_to :site
  attr_accessible :date, :value, :vindex, :source, :meter, :site

  # validate do |reading|

  # 	previous = reading.previous_reading
  # 	nextr = reading.next_reading

  # 	reading.date >= reading.meter.installed_at &&
  # 	reading.value >= reading.meter.offset &&
  # 	reading.value >= previous.value if reading.previous &&
  # 	reading.value <= nextr.value if nextr

  # end

  validates_presence_of :date, :value, :meter, :site, :source
  validates_uniqueness_of :date, :scope => :meter_id
  validates_inclusion_of :source, :in => %w(manual imported computed)
  validate :date_cannot_be_before_meter_installation,
  	:value_cannot_be_less_than_meter_offset,
  	:value_cannot_be_less_than_previous_reading,
    :compute_vindex

  def compute_vindex
    previous = previous_reading
    if previous.nil?
      self.vindex = 0
    else
      if previous.meter_id == self.meter_id
        self.vindex = previous.vindex + (self.value - previous.value)
      else
        self.vindex = previous.vindex + (self.value - self.meter.offset)
      end
    end
    self.vindex
  end

  def date_cannot_be_before_meter_installation
  	if (date < meter.installed_at)
  		errors.add :date, "Date cannot be before meter installation"
  	end
  end

  def value_cannot_be_less_than_meter_offset
  	if (value < meter.offset)
  		errors.add :value, "Value cannot be less than meter offset"
  	end
  end

  def value_cannot_be_less_than_previous_reading
  	previous = previous_reading
  	if !previous.nil? && (value < previous.value)
  		errors.add :value, "Value cannot be less then previous reading"
  	end
  end

  def delta
    previous = previous_reading
    if !previous.nil?
      value - previous.value
    else
      value - meter.offset
    end
  end

  def previous_reading
  	site.meter_readings.where("date < :date", { :date => date }).order('date desc').first
  end

  def next_reading
  	site.meter_readings.where("date >= :date", { :date => date+1 }).order('date').first
  end

end
