from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
# Pydantic Models
from pydantic import BaseModel, model_validator
from typing import Optional

class CoordinateModel(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None
    
    model_config = {"extra": "allow"}  # Allow extra fields like 'long'
    
    @model_validator(mode='before')
    @classmethod
    def handle_long_field(cls, data):
        """Map 'long' field to 'lon' if present."""
        if isinstance(data, dict):
            # If 'long' is provided but 'lon' is not, use 'long' value
            if 'long' in data and data.get('lon') is None:
                data['lon'] = data['long']
        return data

class LocationDetailsModel(BaseModel):
    district_name: Optional[str] = None
    city_name: Optional[str] = None
    district_code: Optional[str] = None
    subdistrict_name: Optional[str] = None
    subdistrict_code: Optional[str] = None
    city_code: Optional[str] = None
    province_code: Optional[str] = None
    province_name: Optional[str] = None
    country_name:  Optional[str] = None
    country_code3: Optional[str] = None
    address: Optional[str] = None
    name: Optional[str] = None
    source: Optional[str] = None
    coordinate: Optional[CoordinateModel] = None
    coordinate_subdistrict: Optional[CoordinateModel] = None
    coordinate_city: Optional[CoordinateModel] = None
    coordinate_district: Optional[CoordinateModel] = None
    coordinate_province: Optional[CoordinateModel] = None
    country_coordinate: Optional[CoordinateModel] = None

class CaseDataModel(BaseModel):
    input: str = Field(..., description="Input text for similarity analysis")
    created_at: str = Field(..., description="Creation timestamp in format: YYYY-MM-DD HH:MM:SS +ZZZZ")
    location_details: Optional[LocationDetailsModel] = Field(None, description="Detailed location information")
    report_summary: str = Field(None, description="Summary of the case")
    report_reliability_score: float = Field(0.0, description="Reliability score of the case")
    sketch: Optional[str] = Field(None, description="URL to sketch image")
    raw_message: Optional[str] = Field(None, description="Raw message content")
    id_case: Optional[str] = Field(None, description="Case ID if already exists")
    coordinate: Optional[List[float]] = Field(None, description="Main coordinates as [lon, lat]")
    images: Optional[List[dict]] = Field(default_factory=list, description="List of image URLs")
    audios: Optional[List[dict]] = Field(default_factory=list, description="List of audio URLs")
    videos: Optional[List[dict]] = Field(default_factory=list, description="List of video URLs")
    files: Optional[List[dict]] = Field(default_factory=list, description="List of file URLs")
    first_name: Optional[str] = Field(None, description="Reporter first name")
    username: Optional[str] = Field(None, description="Reporter username")
    id: Optional[str] = Field(None, description="Unique identifier")
    
    @field_validator('created_at')
    @classmethod
    def validate_created_at(cls, v):
        """Validate created_at format"""
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M:%S %z")
            return v
        except ValueError:
            raise ValueError("created_at must be in format: YYYY-MM-DD HH:MM:SS +ZZZZ")
    
    
class InputDataModel(BaseModel):
    score_threshold: float = Field(0.85, description="Score threshold for similarity")
    limit: int = Field(5, description="Limit for number of similar cases")
    radius_coordinate: float = Field(300.0, description="Radius for coordinate search in meters")
    data: CaseDataModel = Field(..., description="Case data to process")
    report_type: Optional[str] = Field("BOM", description="Type of report")

class ProcessingStatusEnum(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PROCESSING = "processing"

class SimilarDataModel(BaseModel):
    similarity_score: float
    payload: Dict[str, Any]
    metadata: Dict[str, Any]

class ProcessingResponseModel(BaseModel):
    status: ProcessingStatusEnum
    message: str
    case_id: Optional[str] = None
    data_id: Optional[str] = None
    score_threshold: Optional[float] = None
    radius_coordinate: Optional[float] = None
    similar_cases_count: Optional[int] = None
    is_new_case: bool
    processing_time: Optional[float] = None
    case_name: Optional[str] = None

class ErrorResponseModel(BaseModel):
    status: ProcessingStatusEnum = ProcessingStatusEnum.ERROR
    message: str
    error_code: Optional[str] = None

class HealthCheckModel(BaseModel):
    status: str
    timestamp: datetime
    service: str

# New models for report functionality
class ReportModel(BaseModel):
    id: str = Field(..., description="Unique report ID")
    case_id: str = Field(..., description="Case ID")
    report_text: str = Field(..., description="Report content")
    created_at: str = Field(..., description="Creation timestamp")
    processed_at: Optional[str] = Field(None, description="Processing timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class GetLatestReportRequest(BaseModel):
    case_id: str = Field(..., description="Case ID to search for")
    start_time: Optional[str] = Field(None, description="Start time filter in format: YYYY-MM-DD HH:MM:SS +ZZZZ")
    end_time: Optional[str] = Field(None, description="End time filter in format: YYYY-MM-DD HH:MM:SS +ZZZZ")
    limit: Optional[int] = Field(10, description="Maximum number of reports to search")

class LatestReportResponse(BaseModel):
    status: str = "success"
    case_id: str
    reports_found: int
    latest_report: Optional[ReportModel] = None
    query_time_range: Optional[Dict[str, str]] = None