import os
import sys
import asyncio
import httpx
import hashlib
from datetime import datetime
from copy import deepcopy
import pytz


from loguru import logger
from langchain_ebdesk.embeddings import EbdeskTEIEmbeddings
from qdrant_client import models
import jmespath
from tqdm import tqdm
import srsly

from source.db_service.qdrant_scv import AsyncQdrantService
from source.agents import CaseNamingAgent
from source.config import settings

TZ = pytz.timezone("Asia/Jakarta")

class CaseSimilarityProcessor:
    def __init__(self):
        self.embeddings = EbdeskTEIEmbeddings(
            endpoint_url=settings.EMBEDDINGS_BASE_URL,
            model_name=settings.EMBEDDINGS_MODEL_NAME,
            bulk=True,
            timeout=60,
            model_kwargs={"truncate": True, "truncation_direction": "Right"},
            async_client=httpx.AsyncClient(timeout=60, limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)),
        )
        self.case_naming_agent = CaseNamingAgent(
            human_prompt="Here are the details of the report:\n\n{report}\n\nPlease provide a concise case name following the specified rules."
        )
        self.qdrant_client = AsyncQdrantService()
        
    async def _find_similar_data(
        self,
        text: str,
        qdrant_filter: models.Filter = None,
        **kwargs
    ):
        try:
            logger.info(f"Finding similar data for text: {text} with qdrant filter {qdrant_filter}")
            similar_data = await self.qdrant_client.search(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                query_vector=await self.embeddings.aembed_query(text),
                query_filter=qdrant_filter,
                **kwargs
            )
            # convert similar_data to list of dict
            final_similar_data = [
                {
                    "similarity_score": hit.score,
                    "payload": hit.payload,
                    "metadata": hit.payload.get("metadata", {}),
                }
                for hit in similar_data
            ]
            return final_similar_data
        except Exception as e:
            logger.error(f"Error finding similar data: {e}")
            return None

    async def get_reports_by_case_id(
        self,
        case_id: str,
        start_timestamp: int = None,
        end_timestamp: int = None,
        limit: int = 100
    ):
        """
        Get all reports for a specific case_id with optional time filtering using Qdrant
        """
        try:
            logger.info(f"Getting reports for case_id: {case_id}")
            
            # Create filter for case_id
            filters = [
                models.FieldCondition(
                    key="id_case",
                    match=models.MatchText(text=case_id)
                )
            ]
            
            # Add time filters if provided
            if start_timestamp or end_timestamp:
                time_filter = {}
                if start_timestamp:
                    time_filter["gte"] = start_timestamp
                if end_timestamp:
                    time_filter["lte"] = end_timestamp
                
                filters.append(
                    models.FieldCondition(
                        key="timestamp",
                        range=models.Range(**time_filter)
                    )
                )
            
            qdrant_filter = models.Filter(must=filters)
            
            # Use scroll to get all matching documents (not similarity search)
            reports = await self.qdrant_client.scroll(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                scroll_filter=qdrant_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False  # We don't need vectors for this query
            )
            
            if reports is None:
                return []
            
            # Extract metadata from each report
            report_data = []
            for point in reports[0]:  # scroll returns tuple (points, next_page_offset)
                if hasattr(point, 'payload') and point.payload:
                    metadata = point.payload.get("metadata", {})
                    if metadata:
                        report_data.append(metadata)
            
            # Sort reports by timestamp (most recent first)
            sorted_report_data = sorted(
                report_data, 
                key=lambda x: x.get("timestamp", 0), 
                reverse=True
            )
            
            logger.info(f"Found {len(sorted_report_data)} reports for case_id: {case_id}")
            return sorted_report_data
            
        except Exception as e:
            logger.error(f"Error getting reports by case_id {case_id}: {e}")
            return []

    async def _insert_to_qdrant(self, data: dict):
        try:
            await self.qdrant_client.upsert(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                points=[
                    models.PointStruct(
                        id=data.get("id"),
                        vector=await self.embeddings.aembed_query(data.get("text")),
                        payload={
                            "metadata": data,
                            "case_name": data.get("case_name"),
                            "page_content": data.get("input"),
                            "page_content_lower": data.get("input").lower(),
                            "coordinate": data.get("coordinate"),
                            "coordinate_subdistrict": data.get("coordinate_subdistrict"),
                            "coordinate_district": data.get("coordinate_district"),
                            "coordinate_city": data.get("coordinate_city"),
                            "coordinate_province": data.get("coordinate_province"),
                            "country_coordinate": data.get("country_coordinate"),
                            "id_case": data.get("id_case"),
                            "district_code": data.get("district_code"),
                            "subdistrict_code": data.get("subdistrict_code"),
                            "city_code": data.get("city_code"),
                            "province_code": data.get("province_code"),
                            "timestamp": data.get("timestamp")
                        }
                    )
                ]
            )
        except Exception as e:
            logger.error(f"Error inserting data to Qdrant: {e}")

    def _generate_case_id(
        self,
        category, 
        location_code: str,
        date_str: str,
        daily_index: str,
        unique_string: str
    ) -> str:
        hash_part = hashlib.sha256(unique_string.encode()).hexdigest()[:4].upper()
        
        # Contoh penggunaan
        # _generate_case_id("BOM", "TSL", "202507", 1, "Gedung Indicator 2025-07-25 09:05")
        # # Output: BOM-TSL-20250725-01-X7F3
        return f"{category}-{location_code}-{date_str}-{daily_index}-{hash_part}"
        
    def _extract_location_data(self, data: dict) -> dict:
        """Extract and normalize location-related fields from input data."""
        # Extract basic fields
        location_data = {
            "id_case": jmespath.search("id_case", data),
            "data_id": jmespath.search("id", data),
            "created_at": jmespath.search("created_at", data),
            "subdistrict_code": jmespath.search("location_details.subdistrict_code", data),
            "district_code": jmespath.search("location_details.district_code", data),
            "city_code": jmespath.search("location_details.city_code", data),
            "province_code": jmespath.search("location_details.province_code", data),
        }
        
        # Extract and normalize main coordinate
        raw_coordinate = jmespath.search("location_details.coordinate", data)
        if raw_coordinate is None:
            raw_coordinate = jmespath.search("coordinate", data)
            if isinstance(raw_coordinate, list) and len(raw_coordinate) == 2:
                raw_coordinate = {"lon": raw_coordinate[0], "lat": raw_coordinate[1]}
            else:
                raw_coordinate = None
        
        location_data["raw_coordinate"] = raw_coordinate
        
        # Extract other coordinates
        location_data["raw_coordinate_subdistrict"] = jmespath.search("location_details.coordinate_subdistrict", data)
        location_data["raw_coordinate_district"] = jmespath.search("location_details.coordinate_district", data)
        location_data["raw_coordinate_city"] = jmespath.search("location_details.coordinate_city", data)
        location_data["raw_coordinate_province"] = jmespath.search("location_details.coordinate_province", data)
        location_data["raw_country_coordinate"] = jmespath.search("location_details.country_coordinate", data)
        
        return location_data
    
    def _normalize_coordinate(self, raw_coord: dict) -> dict:
        """Normalize coordinate format to {lon, lat}."""
        if not raw_coord:
            return None
        return {
            "lon": raw_coord.get("long") if raw_coord.get("long") else raw_coord.get("lon"),
            "lat": raw_coord.get("lat")
        }
    
    def _build_new_data(
        self,
        data: dict,
        data_id: str,
        id_case: str,
        case_name: str,
        timestamp: int,
        coordinate: dict,
        coordinate_subdistrict: dict,
        coordinate_district: dict,
        coordinate_city: dict,
        coordinate_province: dict,
        country_coordinate: dict,
        subdistrict_code: str,
        district_code: str,
        city_code: str,
        province_code: str
    ) -> dict:
        """Build new data object with all required fields."""
        new_data = deepcopy(data)
        new_data["id"] = data_id
        new_data["text"] = data.get("input")
        new_data["coordinate"] = coordinate
        new_data["coordinate_subdistrict"] = coordinate_subdistrict
        new_data["coordinate_district"] = coordinate_district
        new_data["coordinate_city"] = coordinate_city
        new_data["coordinate_province"] = coordinate_province
        new_data["country_coordinate"] = country_coordinate
        new_data["timestamp"] = timestamp
        new_data["id_case"] = id_case
        new_data["case_name"] = case_name
        new_data["district_code"] = district_code
        new_data["subdistrict_code"] = subdistrict_code
        new_data["city_code"] = city_code
        new_data["province_code"] = province_code
        new_data["processed_at"] = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %z")
        return new_data
    
    def _create_qdrant_filter(
        self,
        coordinate: dict = None,
        coordinate_subdistrict: dict = None,
        coordinate_district: dict = None,
        coordinate_city: dict = None,
        timestamp: int = None,
        coordinate_max_radius: float = 5000.0,
        subdistrict_max_radius: float = 10000.0,
        district_max_radius: float = 15000.0,
        city_max_radius: float = 20000.0,
        subdistrict_code: str = None,
        district_code: str = None,
        city_code: str = None,
        province_code: str = None,
    ) -> models.Filter:
        filters = []
        if coordinate:
            filters.append(
                models.FieldCondition(
                    key="coordinate",
                    geo_radius=models.GeoRadius(
                        center=models.GeoPoint(**coordinate),
                        radius=coordinate_max_radius,
                    ),
                )
            )
        if coordinate_subdistrict:
            filters.append(
                models.FieldCondition(
                    key="coordinate_subdistrict",
                    geo_radius=models.GeoRadius(
                        center=models.GeoPoint(**coordinate_subdistrict),
                        radius=subdistrict_max_radius,
                    ),
                )
            )
        if coordinate_district:
            filters.append(
                models.FieldCondition(
                    key="coordinate_district",
                    geo_radius=models.GeoRadius(
                        center=models.GeoPoint(**coordinate_district),
                        radius=district_max_radius,
                    ),
                )
            )
        if coordinate_city:
            filters.append(
                models.FieldCondition(
                    key="coordinate_city",
                    geo_radius=models.GeoRadius(
                        center=models.GeoPoint(**coordinate_city),
                        radius=city_max_radius,
                    ),
                )
            )
        if timestamp:
            filters.append(
                models.FieldCondition(
                    key="timestamp",
                    range=models.Range(
                        gte=timestamp - 86400,  # 1 day before
                        lte=timestamp + 86400,  # 1 day after
                    ),
                )
            )
        if subdistrict_code:
            filters.append(
                models.FieldCondition(
                    key="subdistrict_code",
                    match=models.MatchText(
                        text=subdistrict_code
                    )
                )
            )
        if district_code:
            filters.append(
                models.FieldCondition(
                    key="district_code",
                    match=models.MatchText(
                        text=district_code
                    )
                )
            )
        if city_code:
            filters.append(
                models.FieldCondition(
                    key="city_code",
                    match=models.MatchText(
                        text=city_code
                    )
                )
            )
        if province_code:
            filters.append(
                models.FieldCondition(
                    key="province_code",
                    match=models.MatchText(
                        text=province_code
                    )
                )
            )

        return models.Filter(
            must=filters
        )
        
    def _format_report(
        self,
        data: dict
    ) -> str:
        """Format the report data into a string for case naming."""
        report_parts = []
        report_parts.append(f"Report Type: {data.get('report_type', 'N/A')}")
        report_parts.append(f"Summary: {data.get('summary', 'N/A')}")
        report_parts.append(f"Input: {data.get('input', 'N/A')}")
        report_parts.append(f"Raw Message: {data.get('raw_message', 'N/A')}")
        
        location_details = data.get("location_details") or {}
        location_info = []
        if location_details.get("name"):
            location_info.append(f"Name: {location_details['name']}")
        if location_details.get("city_name"):
            location_info.append(f"City: {location_details['city_name']}")
        if location_details.get("district_name"):
            location_info.append(f"District: {location_details['district_name']}")
        if location_details.get("subdistrict_name"):
            location_info.append(f"Subdistrict: {location_details['subdistrict_name']}")
        
        if location_info:
            report_parts.append("Location Details: " + ", ".join(location_info))

        return "\n".join(report_parts)
    
    async def _generate_case_name(
        self,
        data: dict
    ) -> str:
        """Generate case name using CaseNamingAgent."""
        formatted_report = self._format_report(data)
        case_name_response = await self.case_naming_agent.run(
            report=formatted_report
        )
        # Extract case_name from JSON response
        try:
            case_name = case_name_response
            return case_name
        except Exception as e:
            logger.error(f"Error parsing case name response: {e}")
            raise ValueError(f"Error parsing case name response: {e}")
    
    async def process_data(
        self,
        data: dict,
        score_threshold: float,
        limit: int = 5,
        radius_coordinate: float = 300.0,
        report_type: str = "BOM"
    ):
        try:
            # Extract location data using helper method
            location_data = self._extract_location_data(data)
            
            id_case = location_data["id_case"]
            data_id = location_data["data_id"]
            created_at = location_data["created_at"]
            timestamp = int(datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S %z").timestamp())
            
            # Normalize all coordinates
            coordinate = self._normalize_coordinate(location_data["raw_coordinate"])
            coordinate_subdistrict = self._normalize_coordinate(location_data["raw_coordinate_subdistrict"])
            coordinate_district = self._normalize_coordinate(location_data["raw_coordinate_district"])
            coordinate_city = self._normalize_coordinate(location_data["raw_coordinate_city"])
            coordinate_province = self._normalize_coordinate(location_data["raw_coordinate_province"])
            country_coordinate = self._normalize_coordinate(location_data["raw_country_coordinate"])
            
            subdistrict_code = location_data["subdistrict_code"]
            district_code = location_data["district_code"]
            city_code = location_data["city_code"]
            province_code = location_data["province_code"]
            
            id_string = f"{data.get('input')}-{jmespath.search('location_details.address', data)}-{data.get('created_at')}"
            if not data_id:
                # create id by hashing md5 of input-address-created_at
                data_id = hashlib.md5(id_string.encode()).hexdigest()
            if not id_case:
                id_case = self._generate_case_id(
                    category=report_type,
                    location_code=city_code if city_code else "UNK",
                    date_str=datetime.fromtimestamp(timestamp).strftime("%Y%m"),
                    # daily_index= get the last 2 char from id
                    daily_index=data_id[-2:],
                    unique_string=id_string
                )
            
            # check similarity first to get similar case on the same day by similarity of the text, timestamp, and location
            # create filter
            qdrant_filter = self._create_qdrant_filter(
                timestamp=timestamp,
                coordinate=coordinate,
                subdistrict_code=subdistrict_code,
                coordinate_max_radius=radius_coordinate,
            )

            # Find similar data
            similar_data = await self._find_similar_data(
                text=data.get("input"),
                qdrant_filter=qdrant_filter,
                score_threshold=score_threshold,
                limit=limit
            )

            # Determine if we found similar cases and update id_case and case_name accordingly
            similar_count = 0
            if similar_data and len(similar_data) > 0:
                logger.info(f"Found {len(similar_data)} similar data for {data_id}")
                
                # Get id_case and case_name from the most similar case (index 0)
                # Note: similar_data is already sorted by similarity score from Qdrant
                top_match = similar_data[0].get("payload", {})
                id_case = top_match.get("id_case", id_case)
                existing_case_name = top_match.get("case_name")
                similar_count = len(similar_data)
                
                if existing_case_name:
                    case_name = existing_case_name
                    logger.info(f"Using existing case name '{case_name}' from most similar case (id_case: {id_case})")
                else:
                    logger.warning(f"Existing case {id_case} missing case_name - generating new name")
                    case_name = await self._generate_case_name(data)
                    logger.info(f"Generated new case name '{case_name}' for existing id_case: {id_case}")
                
                logger.info(f"New report created with the same id case: {id_case}")
            else:
                logger.info(f"No similar data found for {data_id}, creating a new case")
                case_name = await self._generate_case_name(data)
                logger.info(f"New case {id_case} created with id {data_id}")
                logger.info(f"Generated new case name: {case_name}")
            
            # Build and insert new data
            new_data = self._build_new_data(
                data=data,
                data_id=data_id,
                id_case=id_case,
                case_name=case_name,
                timestamp=timestamp,
                coordinate=coordinate,
                coordinate_subdistrict=coordinate_subdistrict,
                coordinate_district=coordinate_district,
                coordinate_city=coordinate_city,
                coordinate_province=coordinate_province,
                country_coordinate=country_coordinate,
                subdistrict_code=subdistrict_code,
                district_code=district_code,
                city_code=city_code,
                province_code=province_code
            )
            
            await self._insert_to_qdrant(new_data)
            return new_data, similar_count

        except Exception as e:
            logger.error(f"Error processing data: {e}")
            logger.exception(e)
            return None, 0
        

if __name__ == "__main__":
    processor = CaseSimilarityProcessor()
    # Example data to process
    example_data = {
        "sketch": "https://asura-s3.ebdesk.com/canvas-agents/sketchs/20250807_143151_data_2fa6676a.png",
        "input": "Ada proyek galian juga di seberang bakso adit bintaro sehingga bisa jadi ada korban tambahan",
        "summary": "Ada proyek galian juga di seberang bakso adit bintaro",
        "case_reliability_score": 80.0,
        "raw_message": "/report@intel_report_to_fusion_bot \n\nAda proyek galian juga di seberang bakso adit bintaro sehingga bisa jadi ada korban tambahan",
        "coordinate": [
            106.6866956,
            -6.2677857
        ],
        "location_details": {
            "district_name": "PONDOK AREN",
            "city_name": "KOTA TANGERANG SELATAN",
            "district_code": "367403",
            "subdistrict_name": "PARIGI BARU",
            "subdistrict_code": "3674031009",
            "city_code": "3674",
            "province_code": "36",
            "province_name": "BANTEN",
            "country_coordinate": {
                "lat": -6.226229803341365,
                "lon": 106.86878065255794
            },
            "country_name": "Indonesia",
            "country_code3": "IDN",
            "coordinate_subdistrict": {
                "lon": 106.6863014088721,
                "lat": -6.270888106641258
            },
            "coordinate_city": {
                "lon": 106.707384985857,
                "lat": -6.302120075748746
            },
            "coordinate_district": {
                "lon": 106.7112203347439,
                "lat": -6.2663819961069755
            },
            "coordinate_province": {
                "lon": 106.12247277629737,
                "lat": -6.454388616009747
            },
            "coordinate": {
                "lat": -6.2680494,
                "lon": 106.68715499999999
            },
            "address": "Jl. H. Rasam No.96, Parigi Baru, Kec. Pd. Aren, Kota Tangerang Selatan, Banten 15228",
            "name": "PT. Indonesia Indicator",
            "source": "google maps"
        },
        "images": [
            "https://asura-s3.ebdesk.com/canvas-agents/detection-images/2025/08/07/20250807_143124_a4f56012.jpg"
        ],
        "first_name": "Emier",
        "username": "emieryusuf",
        "created_at": "2025-08-07 14:31:20 +0700"
    }
    
    asyncio.run(processor.process_data(example_data, score_threshold=0.85))