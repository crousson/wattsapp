class CreateMeters < ActiveRecord::Migration
  def change
    create_table :meters do |t|
      t.integer :offset, :default => 0
      t.date :installed_at, :null => false
      t.date :disposed_at
      t.boolean :active, :default => true
      t.references :site

      t.timestamps
    end
    add_index :meters, :site_id
  end
end
