class Meter < ActiveRecord::Base
  belongs_to :site
  has_many :meter_readings
  attr_accessible :disposed_at, :offset, :installed_at, :active, :site

  validates_presence_of :offset, :installed_at, :active, :site
  validate :installed_and_disposed_at_must_be_congruent

  def installed_and_disposed_at_must_be_congruent
  	if disposed_at.nil?
  		unless active
  			errors.add :disposed_at, "Cannot be null if inactive"
  		end
  	else
  		if active
  			errors.add :active, "Cannot be active if disposed"
  		end
  		if disposed_at < installed_at
  			errors.add :disposed_at, "Disposal date cannot be before installation date"
  		end
  	end
  end

end
