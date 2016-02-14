require 'test_helper'

class SiteTest < ActiveSupport::TestCase

  def print_meter_readings(site)
    puts %w(site date reading vindex source).join("\t")
    site.meter_readings.order(:date).each do |r|
      puts [r.site_id, r.date, r.value, r.vindex, r.source].join("\t")
    end
    puts
  end

  setup do
    site = Site.create :name => "Site 1", :category => "PV", :installed_at => DateTime.parse('2016-01-01').to_date
    meter = site.change_meter site.installed_at, 0
    (0..41).each do |i|
      SiteDailyProduction.create :date => site.installed_at+i, :site => site, :production => 10
    end
    MeterReading.create :value => 0, :date => site.installed_at, :site => site, :meter => meter, :source => 'manual'
    MeterReading.create :value => 100, :date => site.installed_at + 9, :site => site, :meter => meter, :source => 'manual'
    MeterReading.create :value => 200, :date => site.installed_at + 19, :site => site, :meter => meter, :source => 'manual'
    meter = site.change_meter site.installed_at + 19, 1000
    MeterReading.create :value => 1100, :date => site.installed_at + 31, :site => site, :meter => meter, :source => 'manual'
    MeterReading.create :value => 1200, :date => site.installed_at + 41, :site => site, :meter => meter, :source => 'manual'
  end

  test "Get production between two readings" do
    site = Site.first
    t1 = MeterReading.find(1)
    t2 = MeterReading.find(2)
    assert site.get_production_between(t1, t2) == 10 * (t2.date - t1.date)
    t1 = MeterReading.find(3)
    t2 = MeterReading.find(4)
    assert site.get_production_between(t1, t2) == 10 * (t2.date - t1.date)
  end

  test "Interpolate between two readings" do
    site = Site.first
    t1 = MeterReading.find(1)
    t2 = MeterReading.find(2)
    site.interpolate_between(t1, t2)
    next_ = t1
    (1..8).each do |i|
      next_ = next_.next_reading
      assert next_.source == "computed"
      assert next_.value == t1.value + i*11
      assert next_.vindex == t1.vindex + i*11
    end
    assert next_.next_reading.id == t2.id
  end

  test "Interpolate between two readings, after meter changed" do
    site = Site.first
    t1 = MeterReading.find(3)
    t2 = MeterReading.find(4)
    site.interpolate_between(t1, t2)
    next_ = t1.next_reading
    assert next_.value == 1008
    assert next_.vindex == 208
  end

  test "Compute missing readings" do
    site = Site.first
    site.compute_missing_readings
    print_meter_readings site
  end

end
