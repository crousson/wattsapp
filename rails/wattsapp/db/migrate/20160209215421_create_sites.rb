class CreateSites < ActiveRecord::Migration
  def change
    create_table :sites do |t|
      t.string :name
      t.float :lon
      t.float :lat
      t.string :category
      t.date :installed_at

      t.timestamps
    end
  end
end
