# encoding: UTF-8
# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended to check this file into your version control system.

ActiveRecord::Schema.define(:version => 20160209220840) do

  create_table "meter_readings", :force => true do |t|
    t.date     "date"
    t.integer  "value"
    t.integer  "vindex"
    t.string   "source"
    t.integer  "meter_id"
    t.integer  "site_id"
    t.datetime "created_at", :null => false
    t.datetime "updated_at", :null => false
  end

  add_index "meter_readings", ["meter_id"], :name => "index_meter_readings_on_meter_id"

  create_table "meters", :force => true do |t|
    t.integer  "offset",       :default => 0
    t.date     "installed_at",                   :null => false
    t.date     "disposed_at"
    t.boolean  "active",       :default => true
    t.integer  "site_id"
    t.datetime "created_at",                     :null => false
    t.datetime "updated_at",                     :null => false
  end

  add_index "meters", ["site_id"], :name => "index_meters_on_site_id"

  create_table "site_daily_productions", :force => true do |t|
    t.float    "production"
    t.date     "date"
    t.integer  "site_id"
    t.datetime "created_at", :null => false
    t.datetime "updated_at", :null => false
  end

  add_index "site_daily_productions", ["site_id"], :name => "index_site_daily_productions_on_site_id"

  create_table "sites", :force => true do |t|
    t.string   "name"
    t.float    "lon"
    t.float    "lat"
    t.string   "category"
    t.date     "installed_at"
    t.datetime "created_at",   :null => false
    t.datetime "updated_at",   :null => false
  end

end
