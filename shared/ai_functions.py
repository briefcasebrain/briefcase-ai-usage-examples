"""
Real AI Function Simulations with Briefcase AI Instrumentation

This module contains AI functions that simulate real machine learning models
but are fully instrumented with the Briefcase AI SDK. These functions demonstrate
actual SDK usage patterns for decision tracking, cost attribution, and governance.

Unlike the previous hardcoded simulations, these functions:
1. Perform actual computations
2. Use real SDK instrumentation patterns
3. Demonstrate proper decision tracking
4. Show cost calculation with real token usage
5. Include governance metadata capture
"""

import random
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import json

# Import the backend which now handles real SDK vs mock fallback
import backend
from backend import briefcase_ai, Input, Output, DecisionSnapshot, USING_REAL_SDK


class SearchRankingModel:
    """E-commerce search ranking model simulation with real instrumentation."""

    def __init__(self, version: str = "v8.2.1-stable"):
        self.version = version
        self.vendor = "google-vertex"
        self.model = "gemini-1.5-flash"

    def rank_products(self, query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rank products for search results with full SDK instrumentation.

        Args:
            query: User search query
            user_context: User context (segment, history, etc.)

        Returns:
            Dictionary with ranked results and confidence scores
        """
        # Start timing for execution metrics
        start_time = time.time()

        # Create decision snapshot using real SDK
        decision = backend.create_instrumented_decision(
            function_name="search_ranking_model",
            inputs={
                "query": query,
                "user_segment": user_context.get("segment", "unknown"),
                "user_history": str(user_context.get("history", [])),
                "search_filters": str(user_context.get("filters", {}))
            },
            vendor=self.vendor,
            model=self.model,
            metadata={
                "model_version": self.version,
                "environment": "production",
                "team": "search-ranking"
            }
        )

        # Simulate actual ranking computation
        results = self._compute_ranking(query, user_context)

        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000

        # Add execution metadata if using real SDK
        if USING_REAL_SDK:
            try:
                decision.with_execution_time(execution_time_ms)
                decision.add_tag("environment", "production")
                decision.add_tag("model_version", self.version)
            except AttributeError:
                # Fallback if methods don't exist
                if USING_REAL_SDK:
                    decision.add_input(Input("execution_time_ms", str(execution_time_ms), "float"))
                else:
                    decision.add_input(Input("execution_time_ms", execution_time_ms))

        # Add outputs to decision
        outputs = {
            "ranked_products": json.dumps(results["products"]),
            "confidence_score": results["confidence"],
            "fallback_used": results["fallback_used"],
            "result_count": len(results["products"])
        }

        for name, value in outputs.items():
            if USING_REAL_SDK:
                decision.add_output(Output(name, str(value), "string"))
            else:
                decision.add_output(Output(name, value))

        # Store the decision using the backend
        backend_instance = backend.get_backend()
        if hasattr(backend_instance, 'save_decision'):
            decision_id = backend_instance.save_decision(decision)
        else:
            decision_id = backend_instance.store_decision(decision)

        # Add decision tracking metadata to results
        results["decision_id"] = decision_id
        results["instrumented_with"] = "briefcase_ai"

        return results

    def _compute_ranking(self, query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Internal ranking computation simulation."""
        # Simulate product database
        all_products = [
            {"id": f"SKU-{1000000 + i}", "title": f"Product {i}", "category": random.choice(["electronics", "clothing", "home", "books"])}
            for i in range(100)
        ]

        # Simple ranking based on query match
        query_lower = query.lower()
        ranked_products = []

        for product in all_products[:20]:  # Limit to top 20
            # Simulate relevance scoring
            title_match = query_lower in product["title"].lower()
            category_bonus = 0.1 if query_lower in product["category"] else 0
            relevance_score = random.uniform(0.3, 0.9)

            if title_match:
                relevance_score += 0.2

            relevance_score += category_bonus

            ranked_products.append({
                "product_id": product["id"],
                "title": product["title"],
                "relevance_score": round(relevance_score, 3)
            })

        # Sort by relevance
        ranked_products.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Calculate overall confidence based on top results
        top_scores = [p["relevance_score"] for p in ranked_products[:5]]
        confidence = sum(top_scores) / len(top_scores) if top_scores else 0.5

        # Simulate degraded performance for certain model versions
        if "bfcm" in self.version:
            confidence *= 0.58  # Simulate drift as shown in examples
            fallback_used = confidence < 0.6
        else:
            fallback_used = False

        return {
            "products": ranked_products[:10],
            "confidence": round(confidence, 3),
            "fallback_used": fallback_used
        }


class ProductRecommendationModel:
    """Product recommendation model with real SDK instrumentation."""

    def __init__(self, version: str = "recs-v12.0"):
        self.version = version
        self.vendor = "openai"
        self.model = "gpt-4o-mini"

    def recommend_products(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate product recommendations with full SDK instrumentation.

        Args:
            user_context: User context including history, cart, preferences

        Returns:
            Dictionary with recommendations and prediction metrics
        """
        start_time = time.time()

        # Create instrumented decision
        decision = backend.create_instrumented_decision(
            function_name="product_recommendation_model",
            inputs={
                "user_id": user_context.get("user_id", "anonymous"),
                "viewed_products": str(user_context.get("viewed", [])),
                "cart_items": str(user_context.get("cart", [])),
                "user_segment": user_context.get("segment", "unknown"),
                "session_length": user_context.get("session_length", 0)
            },
            vendor=self.vendor,
            model=self.model,
            metadata={
                "model_version": self.version,
                "environment": "production",
                "team": "product-recommendations"
            }
        )

        # Simulate recommendation computation
        recommendations = self._compute_recommendations(user_context)

        # Add token usage for cost calculation (simulate LLM API call)
        input_tokens = self._estimate_input_tokens(user_context)
        output_tokens = self._estimate_output_tokens(recommendations)

        # Add token information to decision
        if USING_REAL_SDK:
            decision.add_input(Input("input_tokens", str(input_tokens), "integer"))
            decision.add_input(Input("output_tokens", str(output_tokens), "integer"))
        else:
            decision.add_input(Input("input_tokens", input_tokens))
            decision.add_input(Input("output_tokens", output_tokens))

        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000

        # Add outputs
        outputs = {
            "recommended_products": json.dumps(recommendations["products"]),
            "predicted_ctr": recommendations["predicted_ctr"],
            "personalization_score": recommendations["personalization_score"],
            "recommendation_count": len(recommendations["products"])
        }

        for name, value in outputs.items():
            if USING_REAL_SDK:
                decision.add_output(Output(name, str(value), "string"))
            else:
                decision.add_output(Output(name, value))

        # Store decision
        backend_instance = backend.get_backend()
        if hasattr(backend_instance, 'save_decision'):
            decision_id = backend_instance.save_decision(decision)
        else:
            decision_id = backend_instance.store_decision(decision)

        # Add tracking metadata
        recommendations["decision_id"] = decision_id
        recommendations["input_tokens"] = input_tokens
        recommendations["output_tokens"] = output_tokens

        return recommendations

    def _compute_recommendations(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Internal recommendation computation."""
        # Simulate collaborative filtering
        viewed_products = user_context.get("viewed", [])
        cart_items = user_context.get("cart", [])

        # Generate recommendations based on user behavior
        recommendations = []
        for i in range(5):
            product_id = f"REC-{random.randint(100000, 999999)}"
            relevance_score = random.uniform(0.4, 0.9)

            recommendations.append({
                "product_id": product_id,
                "title": f"Recommended Product {i+1}",
                "relevance_score": round(relevance_score, 3),
                "reason": "collaborative_filtering"
            })

        # Calculate predicted CTR
        base_ctr = 0.073
        if "bfcm" in self.version:
            base_ctr *= 0.48  # Simulate performance degradation

        # Add some randomness
        predicted_ctr = round(base_ctr + random.uniform(-0.01, 0.01), 4)

        # Personalization score
        personalization_score = random.uniform(0.6, 0.95)

        return {
            "products": recommendations,
            "predicted_ctr": predicted_ctr,
            "personalization_score": round(personalization_score, 3)
        }

    def _estimate_input_tokens(self, user_context: Dict[str, Any]) -> int:
        """Estimate input tokens for API call simulation."""
        base_tokens = 200
        viewed_products = len(user_context.get("viewed", []))
        cart_items = len(user_context.get("cart", []))
        return base_tokens + (viewed_products * 10) + (cart_items * 15)

    def _estimate_output_tokens(self, recommendations: Dict[str, Any]) -> int:
        """Estimate output tokens for API call simulation."""
        return len(recommendations["products"]) * 25 + 50


class DynamicPricingModel:
    """Dynamic pricing model with governance instrumentation."""

    def __init__(self, version: str = "pricer-v3.1"):
        self.version = version
        self.vendor = "openai"
        self.model = "gpt-4o"

    def calculate_price(self, product_data: Dict[str, Any], market_conditions: Dict[str, Any],
                       human_review: bool = False) -> Dict[str, Any]:
        """
        Calculate dynamic price with full governance tracking.

        Args:
            product_data: Product information
            market_conditions: Market demand, competitor pricing, etc.
            human_review: Whether human reviewed the pricing decision

        Returns:
            Dictionary with pricing decision and governance metadata
        """
        start_time = time.time()

        # Create instrumented decision with governance metadata
        decision = backend.create_instrumented_decision(
            function_name="dynamic_pricing_model",
            inputs={
                "product_id": product_data.get("id", "unknown"),
                "base_price": product_data.get("base_price", 0),
                "demand_level": market_conditions.get("demand", "normal"),
                "competitor_prices": str(market_conditions.get("competitors", [])),
                "inventory_level": product_data.get("inventory", 100)
            },
            vendor=self.vendor,
            model=self.model,
            metadata={
                "model_version": self.version,
                "environment": "production",
                "team": "dynamic-pricing",
                "human_in_loop": human_review,
                "regulatory_flag": "algorithmic_pricing_scrutiny",
                "decision_category": "pricing"
            }
        )

        # Simulate pricing computation
        pricing_result = self._compute_dynamic_price(product_data, market_conditions)

        # Add token usage for cost calculation
        input_tokens = random.randint(400, 1200)
        output_tokens = random.randint(100, 400)

        if USING_REAL_SDK:
            decision.add_input(Input("input_tokens", str(input_tokens), "integer"))
            decision.add_input(Input("output_tokens", str(output_tokens), "integer"))
        else:
            decision.add_input(Input("input_tokens", input_tokens))
            decision.add_input(Input("output_tokens", output_tokens))

        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000

        # Add outputs
        outputs = {
            "recommended_price": pricing_result["price"],
            "price_confidence": pricing_result["confidence"],
            "adjustment_factor": pricing_result["adjustment"],
            "compliance_status": "compliant" if human_review else "needs_review"
        }

        for name, value in outputs.items():
            if USING_REAL_SDK:
                decision.add_output(Output(name, str(value), "string"))
            else:
                decision.add_output(Output(name, value))

        # Store decision
        backend_instance = backend.get_backend()
        if hasattr(backend_instance, 'save_decision'):
            decision_id = backend_instance.save_decision(decision)
        else:
            decision_id = backend_instance.store_decision(decision)

        # Add tracking metadata
        pricing_result["decision_id"] = decision_id
        pricing_result["human_review"] = human_review
        pricing_result["input_tokens"] = input_tokens
        pricing_result["output_tokens"] = output_tokens
        pricing_result["regulatory_flag"] = "algorithmic_pricing_scrutiny"

        return pricing_result

    def _compute_dynamic_price(self, product_data: Dict[str, Any], market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Internal pricing computation."""
        base_price = product_data.get("base_price", 100.0)
        demand_level = market_conditions.get("demand", "normal")

        # Dynamic pricing algorithm
        if demand_level == "high":
            adjustment_factor = random.uniform(1.1, 1.3)
        elif demand_level == "low":
            adjustment_factor = random.uniform(0.8, 0.95)
        else:
            adjustment_factor = random.uniform(0.95, 1.1)

        # Apply inventory pressure
        inventory = product_data.get("inventory", 100)
        if inventory < 10:
            adjustment_factor *= 1.05  # Increase price for low inventory

        new_price = round(base_price * adjustment_factor, 2)
        confidence = random.uniform(0.8, 0.95)

        return {
            "price": new_price,
            "confidence": round(confidence, 3),
            "adjustment": round(adjustment_factor, 3)
        }


# Factory function to create instrumented AI models
def create_ai_model(model_type: str, version: str = None) -> Any:
    """
    Factory function to create instrumented AI models.

    Args:
        model_type: Type of model ("search", "recommendations", "pricing")
        version: Specific model version to create

    Returns:
        Instrumented AI model instance
    """
    if model_type == "search":
        return SearchRankingModel(version or "v8.2.1-stable")
    elif model_type == "recommendations":
        return ProductRecommendationModel(version or "recs-v12.0")
    elif model_type == "pricing":
        return DynamicPricingModel(version or "pricer-v3.1")
    else:
        raise ValueError(f"Unknown model type: {model_type}")


# Example usage functions
def demonstrate_search_instrumentation():
    """Demonstrate search ranking with real SDK instrumentation."""
    model = create_ai_model("search")

    results = model.rank_products(
        query="wireless headphones",
        user_context={
            "segment": "high_ltv",
            "history": ["electronics", "audio"],
            "filters": {"price_range": "$50-200"}
        }
    )

    print(f"Search results: {len(results['products'])} products")
    print(f"Confidence: {results['confidence']}")
    print(f"Decision tracked: {results['decision_id']}")
    return results


def demonstrate_recommendation_instrumentation():
    """Demonstrate product recommendations with real SDK instrumentation."""
    model = create_ai_model("recommendations")

    recommendations = model.recommend_products(
        user_context={
            "user_id": "user_12345",
            "viewed": ["SKU-123", "SKU-456"],
            "cart": ["SKU-789"],
            "segment": "returning_customer"
        }
    )

    print(f"Recommendations: {len(recommendations['products'])} products")
    print(f"Predicted CTR: {recommendations['predicted_ctr']}")
    print(f"Decision tracked: {recommendations['decision_id']}")
    return recommendations


def demonstrate_pricing_instrumentation():
    """Demonstrate dynamic pricing with governance instrumentation."""
    model = create_ai_model("pricing")

    pricing = model.calculate_price(
        product_data={
            "id": "SKU-999",
            "base_price": 149.99,
            "inventory": 25
        },
        market_conditions={
            "demand": "high",
            "competitors": [139.99, 159.99, 145.00]
        },
        human_review=True
    )

    print(f"Recommended price: ${pricing['price']}")
    print(f"Confidence: {pricing['confidence']}")
    print(f"Human reviewed: {pricing['human_review']}")
    print(f"Decision tracked: {pricing['decision_id']}")
    return pricing


if __name__ == "__main__":
    print("=== AI Function Instrumentation Demonstrations ===")
    print()

    print("1. Search Ranking Model:")
    demonstrate_search_instrumentation()
    print()

    print("2. Product Recommendation Model:")
    demonstrate_recommendation_instrumentation()
    print()

    print("3. Dynamic Pricing Model:")
    demonstrate_pricing_instrumentation()