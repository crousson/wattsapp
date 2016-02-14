class CreateSiteDailyProductions < ActiveRecord::Migration
  def change
    create_table :site_daily_productions do |t|
      t.float :production
      t.date :date
      t.references :site

      t.timestamps
    end
    add_index :site_daily_productions, :site_id
  end
end
