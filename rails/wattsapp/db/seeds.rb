# This file should contain all the record creation needed to seed the database with its default values.
# The data can then be loaded with the rake db:seed (or created alongside the db with db:setup).
#
# Examples:
#
#   cities = City.create([{ name: 'Chicago' }, { name: 'Copenhagen' }])
#   Mayor.create(name: 'Emanuel', city: cities.first)

site = Site.create :name => "Site 1", :category => "PV", :installed_at => DateTime.parse('2016-01-01').to_date
meter = site.change_meter site.installed_at, 0
(0..41).each {|i| SiteDailyProduction.create :date => site.installed_at+i, :site => site, :production => 10 }
MeterReading.create :value => 0, :date => site.installed_at, :site => site, :meter => meter, :source => 'manual'
MeterReading.create :value => 100, :date => site.installed_at + 9, :site => site, :meter => meter, :source => 'manual'
MeterReading.create :value => 200, :date => site.installed_at + 19, :site => site, :meter => meter, :source => 'manual'
meter = site.change_meter site.installed_at + 19, 1000
MeterReading.create :value => 1100, :date => site.installed_at + 31, :site => site, :meter => meter, :source => 'manual'
MeterReading.create :value => 1200, :date => site.installed_at + 41, :site => site, :meter => meter, :source => 'manual'