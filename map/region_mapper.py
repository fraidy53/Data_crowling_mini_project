"""
데이터베이스 지역명과 GeoJSON 지역명 매핑
"""

# 데이터베이스 지역명 → GeoJSON 지역명 매핑
REGION_MAPPING = {
    '서울': ['Seoul'],
    '경기도': ['Gyeonggi-do', 'Incheon'],  # 인천도 경기권으로 포함
    '강원도': ['Gangwon-do'],
    '충청도': ['Chungcheongbuk-do', 'Chungcheongnam-do', 'Daejeon', 'Sejong'],  # 대전, 세종도 포함
    '경상도': ['Gyeongsangbuk-do', 'Gyeongsangnam-do', 'Busan', 'Daegu', 'Ulsan'],  # 부산, 대구, 울산 포함
    '전라도': ['Jeollabuk-do', 'Jeollanam-do', 'Gwangju']  # 광주 포함 (제주 제외)
}

# GeoJSON 지역명 → 데이터베이스 지역명 매핑 (역매핑)
GEOJSON_TO_DB_REGION = {}
for db_region, geojson_regions in REGION_MAPPING.items():
    for geojson_region in geojson_regions:
        GEOJSON_TO_DB_REGION[geojson_region] = db_region


def get_geojson_regions(db_region):
    """
    데이터베이스 지역명으로 GeoJSON 지역명 리스트 가져오기
    
    Args:
        db_region: 데이터베이스의 지역명 (예: '서울', '경기도')
        
    Returns:
        list: GeoJSON 파일의 지역명 리스트
    """
    return REGION_MAPPING.get(db_region, [])


def get_db_region(geojson_region):
    """
    GeoJSON 지역명으로 데이터베이스 지역명 가져오기
    
    Args:
        geojson_region: GeoJSON 파일의 지역명 (예: 'Seoul', 'Gyeonggi-do')
        
    Returns:
        str: 데이터베이스의 지역명
    """
    return GEOJSON_TO_DB_REGION.get(geojson_region)


def get_all_db_regions():
    """모든 데이터베이스 지역명 리스트"""
    return list(REGION_MAPPING.keys())


def get_all_geojson_regions():
    """모든 GeoJSON 지역명 리스트"""
    return list(GEOJSON_TO_DB_REGION.keys())


# 테스트
if __name__ == '__main__':
    print("=== 지역 매핑 테스트 ===\n")
    
    print("DB 지역 → GeoJSON 지역:")
    for db_region in get_all_db_regions():
        geojson_regions = get_geojson_regions(db_region)
        print(f"  {db_region}: {geojson_regions}")
    
    print("\nGeoJSON 지역 → DB 지역:")
    for geojson_region in ['Seoul', 'Gyeonggi-do', 'Gangwon-do', 'Busan']:
        db_region = get_db_region(geojson_region)
        print(f"  {geojson_region}: {db_region}")
