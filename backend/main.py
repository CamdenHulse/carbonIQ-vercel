﻿"""
NYC CO₂ Sustainability Simulation - FastAPI Backend
Handles data fetching, processing, and AI-powered prompt interpretation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import numpy as np
import json
from dotenv import load_dotenv
import os

from data_processor import NYCEmissionsData
from ai_processor import AIPromptProcessor

# Load environment variables
load_dotenv()

app = FastAPI(title="CO₂UNT API", description="AI-Powered Climate Impact Simulator for NYC")

# CORS middleware for frontend communication
# Get allowed origins from environment variable or use default
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Configure via ALLOWED_ORIGINS env var
    allow_credentials=False,  # Set to False when allowing all origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize data processor
emissions_data = NYCEmissionsData()
ai_processor = AIPromptProcessor()  # Uses ANTHROPIC_API_KEY from environment


class SimulationRequest(BaseModel):
    prompt: str


class GridPoint(BaseModel):
    lat: float
    lon: float
    value: float


class BaselineResponse(BaseModel):
    grid: List[GridPoint]
    metadata: Dict


class SimulationResponse(BaseModel):
    grid: List[GridPoint]
    intervention: Dict
    metadata: Dict
    statistics: Optional[Dict] = None  # Real emissions calculations


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CO₂UNT API",
        "app_name": "CO₂UNT - NYC Climate Impact Simulator",
        "version": "1.0.0"
    }


@app.get("/api/baseline", response_model=BaselineResponse)
async def get_baseline():
    """
    Returns baseline NYC CO2 emissions grid
    
    Combines real OpenAQ station data with synthetic gridded emissions
    based on NYC geography and known emission patterns
    """
    try:
        # Fetch and process baseline data (already filtered to NYC boundaries)
        baseline_grid = emissions_data.get_baseline_grid()
        
        # Convert to response format and calculate statistics
        grid_points = []
        total_intensity = 0
        for lat, lon, value in baseline_grid:
            grid_points.append({
                "lat": float(lat),
                "lon": float(lon),
                "value": float(value)
            })
            total_intensity += value
        
        # Calculate statistics
        num_points = len(grid_points)
        avg_intensity = total_intensity / num_points if num_points > 0 else 0
        
        # Calculate actual total emissions and coverage (intensity × area per cell)
        cell_area_km2 = emissions_data.get_cell_area_km2()
        total_emissions_per_day = total_intensity * cell_area_km2
        coverage_area_km2 = num_points * cell_area_km2
        annual_emissions = total_emissions_per_day * 365
        
        metadata = {
            "city": "New York City",
            "unit": "tonnes COâ‚‚/kmÂ²/day",
            "source": "Calibrated to NYC GHG Inventory (55M tonnes/year)",
            "bounds": {
                "south": 40.49,
                "north": 40.92,
                "west": -74.26,
                "east": -73.70
            },
            "timestamp": emissions_data.get_last_update_time(),
            "datapoints": num_points,
            "coverage_area_km2": round(coverage_area_km2, 1),
            "cell_area_km2": round(cell_area_km2, 4),
            "average_emission_intensity": round(avg_intensity, 2),
            "total_emissions_per_day": round(total_emissions_per_day, 0),
            "annual_emissions_tonnes": round(annual_emissions, 0),
            "description": f"Each datapoint represents ~{cell_area_km2:.2f} km² of NYC. Total coverage: {coverage_area_km2:.0f} km² (NYC land + water)"
        }
        
        return {
            "grid": grid_points,
            "metadata": metadata
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching baseline data: {str(e)}")


@app.post("/api/simulate", response_model=SimulationResponse)
async def simulate_intervention(request: SimulationRequest):
    """
    Processes natural language prompt and returns simulated emissions grid
    
    Uses AI to parse the prompt and apply emissions reductions to relevant areas
    """
    try:
        # Parse the prompt using AI
        intervention = ai_processor.parse_prompt(request.prompt)
        
        # Apply the intervention to the emissions grid
        simulated_grid = emissions_data.apply_intervention(intervention)
        
        # Convert to response format and calculate statistics
        grid_points = []
        total_intensity = 0
        for lat, lon, value in simulated_grid:
            grid_points.append({
                "lat": float(lat),
                "lon": float(lon),
                "value": float(value)
            })
            total_intensity += value
        
        # Calculate statistics
        num_points = len(grid_points)
        avg_intensity = total_intensity / num_points if num_points > 0 else 0
        
        # Calculate actual total emissions and coverage (intensity × area per cell)
        cell_area_km2 = emissions_data.get_cell_area_km2()
        total_emissions_per_day = total_intensity * cell_area_km2
        coverage_area_km2 = num_points * cell_area_km2
        annual_emissions = total_emissions_per_day * 365
        
        metadata = {
            "city": "New York City",
            "unit": "tonnes COâ‚‚/kmÂ²/day",
            "source": "Simulated (NYC boundaries only)",
            "bounds": {
                "south": 40.49,
                "north": 40.92,
                "west": -74.26,
                "east": -73.70
            },
            "timestamp": emissions_data.get_last_update_time(),
            "datapoints": num_points,
            "coverage_area_km2": round(coverage_area_km2, 1),
            "cell_area_km2": round(cell_area_km2, 4),
            "average_emission_intensity": round(avg_intensity, 2),
            "total_emissions_per_day": round(total_emissions_per_day, 0),
            "annual_emissions_tonnes": round(annual_emissions, 0),
            "description": f"Each datapoint represents ~{cell_area_km2:.2f} km² of NYC. Total coverage: {coverage_area_km2:.0f} km² (NYC land + water)"
        }
        
        # Extract real emissions statistics if available
        statistics = None
        if 'real_emissions' in intervention:
            statistics = intervention['real_emissions']
            print(f"[API] Including real emissions statistics in response")
            print(f"[API] Statistics: baseline={statistics.get('baseline_tons_co2')}, reduced={statistics.get('reduced_tons_co2')}, percentage={statistics.get('percentage_reduction')}%")

        # Debug: Log what we're sending to frontend
        print(f"[API] Sending to frontend:")
        print(f"      intervention.reduction_percent = {intervention.get('reduction_percent')}")
        print(f"      intervention.direction = {intervention.get('direction')}")
        print(f"      statistics.percentage_reduction = {statistics.get('percentage_reduction') if statistics else 'N/A'}")

        return {
            "grid": grid_points,
            "intervention": intervention,
            "metadata": metadata,
            "statistics": statistics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating intervention: {str(e)}")


@app.get("/api/openaq")
async def get_openaq_stations():
    """
    Returns raw OpenAQ station data for NYC
    Useful for debugging and transparency
    """
    try:
        stations = emissions_data.fetch_openaq_data()
        return {
            "stations": stations,
            "count": len(stations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching OpenAQ data: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"[START] Starting CarbonIQ API on port {port}")
    print(f"[INFO] CarbonIQ - AI-Powered Climate Impact Simulator")
    print(f"[URL] API Documentation: http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)


