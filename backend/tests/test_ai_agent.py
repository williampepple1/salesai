import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.ai_agent import AIAgent
from app.models import User, Product


@pytest.fixture
def ai_agent():
    """Create AI agent instance"""
    return AIAgent()


@pytest.fixture
def test_products(db):
    """Create test products"""
    user = User(
        id=1,
        email="test@example.com",
        username="testuser",
        business_name="Test Store"
    )
    db.add(user)
    
    products = [
        Product(
            id=1,
            user_id=1,
            name="Laptop",
            description="High-performance laptop",
            price=999.99,
            stock_quantity=5,
            is_available=True
        ),
        Product(
            id=2,
            user_id=1,
            name="Wireless Mouse",
            description="Ergonomic wireless mouse",
            price=29.99,
            stock_quantity=20,
            is_available=True
        )
    ]
    
    for product in products:
        db.add(product)
    
    db.commit()
    return products


def test_system_prompt_includes_boundaries(ai_agent, test_products):
    """Test that system prompt includes strict boundaries"""
    user = User(
        username="testuser",
        business_name="Test Store"
    )
    
    prompt = ai_agent.generate_system_prompt(user, test_products)
    
    # Check for critical boundary keywords
    assert "CRITICAL BOUNDARIES" in prompt
    assert "ONLY discuss products from the catalog" in prompt
    assert "NEVER discuss topics unrelated" in prompt
    assert "DECLINE politely" in prompt
    assert "DO NOT engage in general conversation" in prompt
    
    # Check that products are listed
    assert "Laptop" in prompt
    assert "Wireless Mouse" in prompt


def test_system_prompt_with_no_products(ai_agent):
    """Test system prompt when no products available"""
    user = User(
        username="testuser",
        business_name="Test Store"
    )
    
    prompt = ai_agent.generate_system_prompt(user, [])
    
    assert "No products available" in prompt
    assert "CRITICAL BOUNDARIES" in prompt


def test_is_response_on_topic_valid_product_discussion(ai_agent, test_products):
    """Test that product-related responses are marked as on-topic"""
    response = "The Laptop is available for $999.99. It's a high-performance device perfect for your needs."
    
    assert ai_agent._is_response_on_topic(response, test_products) is True


def test_is_response_on_topic_off_topic_politics(ai_agent, test_products):
    """Test that political discussions are marked as off-topic"""
    response = "Let me tell you about the current political situation and how it affects the economy."
    
    assert ai_agent._is_response_on_topic(response, test_products) is False


def test_is_response_on_topic_off_topic_news(ai_agent, test_products):
    """Test that news discussions are marked as off-topic"""
    response = "Did you hear about the latest news regarding the celebrity scandal?"
    
    assert ai_agent._is_response_on_topic(response, test_products) is False


def test_is_response_on_topic_off_topic_health(ai_agent, test_products):
    """Test that health advice is marked as off-topic"""
    response = "I can provide you with medical advice for your condition."
    
    assert ai_agent._is_response_on_topic(response, test_products) is False


def test_is_response_on_topic_short_greeting(ai_agent, test_products):
    """Test that short greetings are allowed"""
    response = "Hello! How can I help you today?"
    
    assert ai_agent._is_response_on_topic(response, test_products) is True


def test_is_response_on_topic_order_related(ai_agent, test_products):
    """Test that order-related responses are on-topic"""
    response = "I've added 2 items to your cart. Your total is $59.98. Would you like to proceed with the order?"
    
    assert ai_agent._is_response_on_topic(response, test_products) is True


def test_fallback_response_generation(ai_agent, test_products):
    """Test fallback response when AI goes off-topic"""
    user = User(
        username="testuser",
        business_name="Test Store"
    )
    
    fallback = ai_agent._get_fallback_response("Test Store", test_products)
    
    assert "Test Store" in fallback
    assert "Laptop" in fallback or "Wireless Mouse" in fallback
    assert "products" in fallback.lower()


def test_fallback_response_no_products(ai_agent):
    """Test fallback response when no products available"""
    fallback = ai_agent._get_fallback_response("Test Store", [])
    
    assert "Test Store" in fallback
    assert "no products available" in fallback.lower()


def test_function_definitions_structure(ai_agent):
    """Test that function definitions are properly structured"""
    functions = ai_agent.get_function_definitions()
    
    assert len(functions) == 4
    
    function_names = [f["name"] for f in functions]
    assert "get_product_details" in function_names
    assert "calculate_price" in function_names
    assert "add_to_cart" in function_names
    assert "create_order" in function_names
    
    # Check each function has required fields
    for func in functions:
        assert "name" in func
        assert "description" in func
        assert "parameters" in func
        assert "type" in func["parameters"]
        assert "properties" in func["parameters"]


@pytest.mark.asyncio
@patch('app.services.ai_agent.OpenAI')
async def test_off_topic_response_gets_replaced(mock_openai_class, ai_agent, db, test_products):
    """Test that off-topic responses are replaced with fallback"""
    # Mock OpenAI to return an off-topic response
    mock_client = Mock()
    mock_openai_class.return_value = mock_client
    
    mock_response = Mock()
    mock_message = Mock()
    mock_message.content = "Let me tell you about the weather today and some political news."
    mock_message.function_call = None
    mock_response.choices = [Mock(message=mock_message)]
    
    mock_client.chat.completions.create.return_value = mock_response
    
    # Create test data
    user = User(
        id=1,
        email="test@example.com",
        username="testuser",
        business_name="Test Store",
        hashed_password="hashed"
    )
    db.add(user)
    
    from app.models import Conversation
    conversation = Conversation(
        id=1,
        user_id=1,
        telegram_chat_id="123",
        messages=[]
    )
    db.add(conversation)
    db.commit()
    
    # Recreate agent with mocked client
    agent = AIAgent()
    agent.client = mock_client
    
    result = await agent.process_message(
        message="Tell me about the weather",
        conversation_id=1,
        user_id=1,
        db=db
    )
    
    # The off-topic response should be replaced with fallback
    assert "Test Store" in result["response"]
    assert "products" in result["response"].lower()
    assert "weather" not in result["response"].lower()


def test_off_topic_keywords_list(ai_agent):
    """Test that off-topic keywords are properly defined"""
    assert len(ai_agent.off_topic_keywords) > 0
    assert "politics" in ai_agent.off_topic_keywords
    assert "news" in ai_agent.off_topic_keywords
    assert "health advice" in ai_agent.off_topic_keywords
    assert "medical" in ai_agent.off_topic_keywords
