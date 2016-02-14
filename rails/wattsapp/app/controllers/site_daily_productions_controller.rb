class SiteDailyProductionsController < ApplicationController
  # GET /site_daily_productions
  # GET /site_daily_productions.json
  def index
    @site_daily_productions = SiteDailyProduction.all

    respond_to do |format|
      format.html # index.html.erb
      format.json { render json: @site_daily_productions }
    end
  end

  # GET /site_daily_productions/1
  # GET /site_daily_productions/1.json
  def show
    @site_daily_production = SiteDailyProduction.find(params[:id])

    respond_to do |format|
      format.html # show.html.erb
      format.json { render json: @site_daily_production }
    end
  end

  # GET /site_daily_productions/new
  # GET /site_daily_productions/new.json
  def new
    @site_daily_production = SiteDailyProduction.new

    respond_to do |format|
      format.html # new.html.erb
      format.json { render json: @site_daily_production }
    end
  end

  # GET /site_daily_productions/1/edit
  def edit
    @site_daily_production = SiteDailyProduction.find(params[:id])
  end

  # POST /site_daily_productions
  # POST /site_daily_productions.json
  def create
    @site_daily_production = SiteDailyProduction.new(params[:site_daily_production])

    respond_to do |format|
      if @site_daily_production.save
        format.html { redirect_to @site_daily_production, notice: 'Site daily production was successfully created.' }
        format.json { render json: @site_daily_production, status: :created, location: @site_daily_production }
      else
        format.html { render action: "new" }
        format.json { render json: @site_daily_production.errors, status: :unprocessable_entity }
      end
    end
  end

  # PUT /site_daily_productions/1
  # PUT /site_daily_productions/1.json
  def update
    @site_daily_production = SiteDailyProduction.find(params[:id])

    respond_to do |format|
      if @site_daily_production.update_attributes(params[:site_daily_production])
        format.html { redirect_to @site_daily_production, notice: 'Site daily production was successfully updated.' }
        format.json { head :no_content }
      else
        format.html { render action: "edit" }
        format.json { render json: @site_daily_production.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /site_daily_productions/1
  # DELETE /site_daily_productions/1.json
  def destroy
    @site_daily_production = SiteDailyProduction.find(params[:id])
    @site_daily_production.destroy

    respond_to do |format|
      format.html { redirect_to site_daily_productions_url }
      format.json { head :no_content }
    end
  end
end
