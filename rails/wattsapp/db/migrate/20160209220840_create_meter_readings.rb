class CreateMeterReadings < ActiveRecord::Migration
  def change
    create_table :meter_readings do |t|
      t.date :date
      t.integer :value
      t.integer :vindex
      t.string :source
      t.references :meter
      t.references :site

      t.timestamps
    end
    add_index :meter_readings, :meter_id
  end
end
