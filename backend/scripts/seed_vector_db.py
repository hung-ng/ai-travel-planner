"""
Seed ChromaDB with travel knowledge
"""
import sys
from pathlib import Path
import asyncio

sys.path.append(str(Path(__file__).parent.parent))

from app.services.rag_service import rag_service

async def seed_knowledge():
    """Add travel information to vector DB"""
    
    print("🌱 Seeding vector database...")
    
    # Paris travel documents
    documents = [
        # 1. Overview
        """Paris, the capital of France, is one of the world's most visited cities. 
        Famous for the Eiffel Tower, Louvre Museum, Notre-Dame Cathedral, Arc de Triomphe, 
        and charming neighborhoods like Montmartre, Le Marais, and Latin Quarter. 
        The city has 20 arrondissements (districts), each with unique character.""",
        
        # 2. Best time to visit
        """Best time to visit Paris: April-June and September-October offer mild weather 
        (15-25°C), fewer crowds than summer, and blooming gardens. Spring brings cherry 
        blossoms, autumn offers golden foliage. Avoid August when locals vacation and 
        many shops close. Winter (Dec-Feb) is cold but magical with Christmas markets.""",
        
        # 3. Top museums
        """Paris museums: The Louvre is the world's largest art museum, home to Mona Lisa, 
        Venus de Milo, and 35,000+ artworks. Book morning time slots online. Musée d'Orsay 
        showcases Impressionist masterpieces in a beautiful Beaux-Arts train station. 
        Musée de l'Orangerie displays Monet's Water Lilies. Rodin Museum has sculptures 
        and peaceful gardens. Consider Paris Museum Pass (€62 for 2 days, covers 60+ museums).""",
        
        # 4. Food scene
        """Paris food: Le Marais (4th arr) has excellent bistros like L'As du Fallafel and 
        Chez Janou. Latin Quarter offers traditional brasseries and student-friendly cafés. 
        Visit neighborhood markets like Marché Bastille or Marché des Enfants Rouges (oldest 
        covered market). Try prix fixe lunch menus (€15-25) for good value. Essential foods: 
        fresh croissants from boulangeries, cheese plates, steak frites, macarons from 
        Ladurée or Pierre Hermé.""",
        
        # 5. Transportation
        """Paris metro system has 16 lines covering the entire city. Operating hours: 
        5:30am-1am weekdays, until 2am weekends. Buy Navigo Découverte pass (€30/week unlimited) 
        or carnet of 10 tickets (€17). Central areas are walkable. Vélib' bike sharing available. 
        Avoid taxis, use metro or Uber instead. From CDG Airport: RER B train (€11, 45 min) 
        or Roissybus (€14, 60 min).""",
        
        # 6. 5-day itinerary
        """5-day Paris itinerary: Day 1 - Eiffel Tower area, Trocadéro gardens, Seine river cruise. 
        Day 2 - Louvre morning (book tickets!), Tuileries Garden, Champs-Élysées, Arc de Triomphe. 
        Day 3 - Montmartre, Sacré-Cœur, artists' square, Moulin Rouge area. Day 4 - Musée d'Orsay, 
        Latin Quarter, Notre-Dame island, Saint-Germain-des-Prés. Day 5 - Le Marais district, 
        Centre Pompidou, Marché des Enfants Rouges, evening at Canal Saint-Martin.""",
        
        # 7. Budget guide
        """Paris budget per day: Budget travel (€80-120): hostels, street food, free attractions, 
        walking tours. Mid-range (€150-250): 3-star hotels, bistro meals, museum entries, 
        occasional taxi. Luxury (€400+): 4-5 star hotels, Michelin restaurants, private tours. 
        Typical costs: hotel €100-200, breakfast €8-15, lunch €15-30, dinner €30-70, 
        metro day pass €15, museum entry €12-20.""",
        
        # 8. Hidden gems
        """Paris hidden gems: Canal Saint-Martin - trendy area with waterside cafés, local vibe. 
        Promenade Plantée - elevated park walkway (inspired NYC's High Line). Sainte-Chapelle - 
        stunning 13th-century stained glass, often overlooked. Père Lachaise Cemetery - peaceful 
        walks, famous graves (Jim Morrison, Oscar Wilde, Chopin). Rue Crémieux - colorful 
        Instagram street. Shakespeare and Company bookshop - iconic English bookstore.""",
        
        # 9. Food experiences
        """Must-try Paris food experiences: Authentic croissant from Du Pain et des Idées or 
        Gontran Cherrier (not chain bakeries). Cheese tasting at fromagerie with wine pairing. 
        Classic steak frites at traditional bistro like Le Relais de l'Entrecôte. Fresh oysters 
        at seafood bars near Montparnasse. Macarons from Ladurée or Pierre Hermé. Market picnic 
        with baguette, cheese, wine, charcuterie. Hot chocolate at Angelina (thick, rich). 
        Wine tasting in natural wine bars of 10th/11th arrondissements.""",
        
        # 10. Practical tips
        """Paris practical tips: Learn basic French (bonjour, merci, s'il vous plaît, pardon). 
        Most museums closed Mondays or Tuesdays - check before visiting. Book popular restaurants 
        2-3 days ahead. Buy Louvre and Versailles tickets online to skip lines. Be aware of 
        pickpockets at tourist sites - keep valuables secure. Tap water (l'eau du robinet) is 
        safe and free at restaurants. Tipping: round up or 5-10% for exceptional service 
        (service is included in prices). Most shops closed Sundays except Marais and Champs-Élysées."""
    ]
    
    metadatas = [
        {"city": "Paris", "topic": "overview", "category": "general"},
        {"city": "Paris", "topic": "timing", "category": "planning"},
        {"city": "Paris", "topic": "museums", "category": "attractions"},
        {"city": "Paris", "topic": "food", "category": "dining"},
        {"city": "Paris", "topic": "transportation", "category": "logistics"},
        {"city": "Paris", "topic": "itinerary", "category": "planning"},
        {"city": "Paris", "topic": "budget", "category": "planning"},
        {"city": "Paris", "topic": "hidden_gems", "category": "attractions"},
        {"city": "Paris", "topic": "food_experiences", "category": "dining"},
        {"city": "Paris", "topic": "tips", "category": "general"}
    ]
    
    ids = [
        "paris_overview",
        "paris_timing",
        "paris_museums",
        "paris_food",
        "paris_transport",
        "paris_itinerary_5day",
        "paris_budget",
        "paris_hidden_gems",
        "paris_food_experiences",
        "paris_tips"
    ]
    
    # Add to ChromaDB
    await rag_service.add_documents(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✅ Successfully added {len(documents)} documents to vector database")
    print("Topics covered: overview, timing, museums, food, transportation, itinerary, budget, hidden gems, tips")

if __name__ == "__main__":
    asyncio.run(seed_knowledge())