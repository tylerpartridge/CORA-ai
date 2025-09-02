#!/usr/bin/env python3
"""
Test BI Registry validation

Validates that registry.yml has the required schema and competitor entries.
"""

import pytest
import yaml
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestBIRegistry:
    """Test BI registry.yml structure and content"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.registry_path = Path(__file__).parent.parent / "docs/bi/registry.yml"
        
    def test_registry_file_exists(self):
        """Test that registry.yml exists"""
        assert self.registry_path.exists(), f"Registry file not found at {self.registry_path}"
    
    def test_registry_is_valid_yaml(self):
        """Test that registry.yml is valid YAML"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            assert data is not None, "Registry YAML is empty"
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in registry: {e}")
    
    def test_registry_has_competitors_section(self):
        """Test that registry has competitors section"""
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        assert 'competitors' in data, "Registry missing 'competitors' section"
        assert isinstance(data['competitors'], list), "Competitors should be a list"
        assert len(data['competitors']) > 0, "Competitors list is empty"
    
    def test_competitor_entries_have_required_fields(self):
        """Test that each competitor has required fields"""
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        required_fields = ['name', 'urls', 'tags']
        
        for idx, competitor in enumerate(data.get('competitors', [])):
            for field in required_fields:
                assert field in competitor, f"Competitor {idx} missing field: {field}"
            
            # Validate field types
            assert isinstance(competitor['name'], str), f"Competitor {idx} name should be string"
            assert isinstance(competitor['urls'], list), f"Competitor {idx} urls should be list"
            assert isinstance(competitor['tags'], list), f"Competitor {idx} tags should be list"
            assert len(competitor['urls']) > 0, f"Competitor {idx} has no URLs"
    
    def test_competitor_urls_are_valid(self):
        """Test that competitor URLs start with http/https"""
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        for competitor in data.get('competitors', []):
            for url in competitor.get('urls', []):
                assert url.startswith(('http://', 'https://')), \
                    f"Invalid URL for {competitor['name']}: {url}"
    
    def test_known_competitors_exist(self):
        """Test that known competitors are in the registry"""
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        competitor_names = [c['name'] for c in data.get('competitors', [])]
        
        # Check for some expected competitors
        expected_competitors = [
            'Contractor Foreman',
            'QuickBooks Online',
            'Zoho Expense'
        ]
        
        for expected in expected_competitors:
            assert expected in competitor_names, f"Expected competitor '{expected}' not found"
    
    def test_regulations_section_if_exists(self):
        """Test regulations_watch section if it exists"""
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if 'regulations_watch' in data:
            assert isinstance(data['regulations_watch'], list), "Regulations should be a list"
            
            for idx, regulation in enumerate(data['regulations_watch']):
                assert 'name' in regulation, f"Regulation {idx} missing name"
                assert 'urls' in regulation, f"Regulation {idx} missing urls"
                assert isinstance(regulation['urls'], list), f"Regulation {idx} urls should be list"
    
    def test_pricing_tags_present(self):
        """Test that pricing tags are used appropriately"""
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        pricing_competitors = 0
        for competitor in data.get('competitors', []):
            if 'pricing' in competitor.get('tags', []):
                pricing_competitors += 1
        
        assert pricing_competitors > 0, "No competitors have 'pricing' tag"
        print(f"Found {pricing_competitors} competitors with pricing info")


def test_registry_schema_completeness():
    """Test that registry has all expected top-level sections"""
    registry_path = Path(__file__).parent.parent / "docs/bi/registry.yml"
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Check for expected sections
    assert 'competitors' in data, "Missing competitors section"
    
    # Optional but good to have
    if 'regulations_watch' in data:
        assert isinstance(data['regulations_watch'], list), "regulations_watch should be a list"


if __name__ == "__main__":
    print("\nTesting BI Registry Validation\n")
    print("-" * 50)
    
    # Run tests
    test_suite = TestBIRegistry()
    
    print("\n1. Testing registry file exists...")
    test_suite.setup_method()
    test_suite.test_registry_file_exists()
    print("   OK: Registry file exists")
    
    print("\n2. Testing valid YAML...")
    test_suite.test_registry_is_valid_yaml()
    print("   OK: Registry is valid YAML")
    
    print("\n3. Testing competitors section...")
    test_suite.test_registry_has_competitors_section()
    print("   OK: Competitors section exists")
    
    print("\n4. Testing competitor fields...")
    test_suite.test_competitor_entries_have_required_fields()
    print("   OK: All competitors have required fields")
    
    print("\n5. Testing URL validity...")
    test_suite.test_competitor_urls_are_valid()
    print("   OK: All URLs are valid")
    
    print("\n6. Testing known competitors...")
    test_suite.test_known_competitors_exist()
    print("   OK: Expected competitors found")
    
    print("\n7. Testing regulations section...")
    test_suite.test_regulations_section_if_exists()
    print("   OK: Regulations section valid (if exists)")
    
    print("\n8. Testing pricing tags...")
    test_suite.test_pricing_tags_present()
    
    print("\n9. Testing schema completeness...")
    test_registry_schema_completeness()
    print("   OK: Registry schema is complete")
    
    print("\n" + "=" * 50)
    print("SUCCESS: All registry validation tests passed!")
    print("=" * 50)