class SiteDailyProduction < ActiveRecord::Base
  belongs_to :site
  attr_accessible :date, :production, :site

  validates_presence_of :date, :production, :site
  validates_uniqueness_of :date, :scope => :site_id
  validates_numericality_of :production, :integer => true, :greater_than_or_equal_to => 0
end
