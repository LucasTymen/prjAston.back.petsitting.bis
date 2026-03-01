import pytest
from unittest.mock import patch, MagicMock
from agents.scraper import ScraperOffre, EntrepriseScraper
from core.models import ScraperOutput

def test_clean_html():
    scraper = ScraperOffre()
    html = "<html><body><h1>Titre</h1><script>alert('test')</script><p>Texte de  l'offre.</p></body></html>"
    clean_text = scraper.clean_html(html)
    assert "Titre" in clean_text
    assert "Texte de l'offre" in clean_text
    assert "alert('test')" not in clean_text

@patch("agents.scraper.requests.get")
def test_scraper_process(mock_get):
    mock_response = MagicMock()
    mock_response.text = "<html><body><h1>Dev Python</h1><p>Nous cherchons un dev.</p></body></html>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    scraper = ScraperOffre()
    
    # Mock LLM extraction
    scraper.extract_with_llm = MagicMock(return_value=ScraperOutput(
        titre="Dev Python",
        entreprise="Unknown",
        description_clean="Dev Python Nous cherchons un dev.",
        mots_cles_detectes=["Python", "Dev"],
        niveau_poste="Junior",
        probleme_detecte="Besoin de code."
    ))

    result = scraper.process("http://example.com/job")
    
    assert mock_get.called
    assert scraper.extract_with_llm.called
    assert isinstance(result, ScraperOutput)
    assert result.titre == "Dev Python"

def test_entreprise_scraper_process():
    scraper = EntrepriseScraper()
    result = scraper.process("http://entreprise.com")
    assert "recrutement@galerie-test.com" in result.get("email_trouve", "")
    assert result.get("niveau_confiance") == "Haute"

def test_extract_with_llm_direct_call():
    # Test internal method with mock data
    scraper = ScraperOffre()
    # Mocking self.llm
    with patch.object(scraper.llm, 'chat_completion', return_value={
        "titre": "Mock Title",
        "entreprise": "Mock Corp",
        "description_clean": "Desc",
        "mots_cles_detectes": ["Python"],
        "niveau_poste": "Junior",
        "probleme_detecte": "None"
    }):
        result = scraper.extract_with_llm("url", "some clean text")
        assert result.titre == "Mock Title"
        assert result.entreprise == "Mock Corp"
