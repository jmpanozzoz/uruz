"""
Ejemplo 5: Agente Autónomo Avanzado de Trading
Este ejemplo muestra un agente de trading que analiza datos del mercado y toma decisiones
de compra/venta de forma autónoma.
"""

from uruz.core.agent import Agent
from uruz.llm.openai_provider import OpenAIProvider
from typing import Dict, List, Any
import asyncio
import random
from datetime import datetime, timedelta

class MarketData:
    """Simula datos del mercado para el ejemplo."""
    def __init__(self):
        self.base_price = 100
        self.volatility = 0.02
        
    def get_current_price(self) -> float:
        """Simula el precio actual con algo de volatilidad."""
        return self.base_price * (1 + random.uniform(-self.volatility, self.volatility))
    
    def get_market_sentiment(self) -> str:
        """Simula el sentimiento del mercado."""
        sentiments = ["bullish", "bearish", "neutral"]
        return random.choice(sentiments)

class TradingAgent(Agent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.llm = OpenAIProvider(config["llm_config"])
        self.market = MarketData()
        self.portfolio = {
            "cash": config.get("initial_cash", 10000),
            "assets": config.get("initial_assets", 0)
        }
        self.last_trade_time = datetime.now()
        self.trade_cooldown = timedelta(minutes=5)
        self.analysis_history = []

    async def analyze_market_conditions(self) -> Dict[str, Any]:
        """Analiza las condiciones actuales del mercado."""
        current_price = self.market.get_current_price()
        market_sentiment = self.market.get_market_sentiment()
        
        # Usar LLM para analizar la situación
        prompt = f"""
        Analiza las siguientes condiciones del mercado y recomienda una acción:
        - Precio actual: ${current_price}
        - Sentimiento del mercado: {market_sentiment}
        - Efectivo disponible: ${self.portfolio['cash']}
        - Activos en posesión: {self.portfolio['assets']}
        
        Responde solo con: COMPRAR, VENDER o MANTENER
        """
        
        recommendation = await self.llm.generate(prompt)
        return {
            "price": current_price,
            "sentiment": market_sentiment,
            "recommendation": recommendation.strip()
        }

    async def execute_trade(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta operaciones de trading basadas en el análisis."""
        price = analysis["price"]
        action = analysis["recommendation"]
        
        if action == "COMPRAR" and self.portfolio["cash"] >= price:
            self.portfolio["cash"] -= price
            self.portfolio["assets"] += 1
            return {
                "type": "trade",
                "action": "COMPRA",
                "price": price,
                "quantity": 1
            }
        elif action == "VENDER" and self.portfolio["assets"] > 0:
            self.portfolio["cash"] += price
            self.portfolio["assets"] -= 1
            return {
                "type": "trade",
                "action": "VENTA",
                "price": price,
                "quantity": 1
            }
        
        return {
            "type": "trade",
            "action": "MANTENER",
            "price": price,
            "quantity": 0
        }

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa mensajes entrantes (por ejemplo, para consultar el estado del portfolio)."""
        if message.get("type") == "status":
            return {
                "type": "status_response",
                "portfolio": self.portfolio,
                "last_analysis": self.analysis_history[-1] if self.analysis_history else None
            }
        return {"type": "error", "content": "Tipo de mensaje no soportado"}

    async def act(self) -> List[Dict[str, Any]]:
        """Realiza acciones autónomas de trading."""
        current_time = datetime.now()
        actions = []
        
        # Verificar si ha pasado suficiente tiempo desde la última operación
        if current_time - self.last_trade_time < self.trade_cooldown:
            return actions

        # Analizar el mercado
        analysis = await self.analyze_market_conditions()
        self.analysis_history.append(analysis)
        
        # Ejecutar operación si es necesario
        trade_result = await self.execute_trade(analysis)
        
        # Registrar acciones
        actions.append({
            "type": "analysis",
            "content": analysis
        })
        
        if trade_result["action"] != "MANTENER":
            actions.append(trade_result)
            self.last_trade_time = current_time
            
        # Agregar resumen del portfolio
        actions.append({
            "type": "portfolio_update",
            "content": {
                "cash": self.portfolio["cash"],
                "assets": self.portfolio["assets"],
                "total_value": self.portfolio["cash"] + (self.portfolio["assets"] * analysis["price"])
            }
        })
        
        return actions

async def main():
    # Configurar y ejecutar el agente de trading
    config = {
        "initial_cash": 10000,
        "initial_assets": 0,
        "llm_config": {
            "api_key": "tu-api-key-aquí",
            "model": "gpt-4"
        }
    }
    
    agent = TradingAgent("trader_001", config)
    
    # Simular 3 ciclos de trading
    print("Iniciando simulación de trading...")
    for i in range(3):
        print(f"\nCiclo de trading {i+1}")
        actions = await agent.act()
        
        for action in actions:
            if action["type"] == "analysis":
                print(f"Análisis: Precio=${action['content']['price']:.2f}, "
                      f"Recomendación={action['content']['recommendation']}")
            elif action["type"] == "trade":
                print(f"Operación: {action['action']} - "
                      f"Precio=${action['price']:.2f}, Cantidad={action['quantity']}")
            elif action["type"] == "portfolio_update":
                print(f"Portfolio: Efectivo=${action['content']['cash']:.2f}, "
                      f"Activos={action['content']['assets']}, "
                      f"Valor Total=${action['content']['total_value']:.2f}")
        
        await asyncio.sleep(2)  # Esperar 2 segundos entre ciclos

if __name__ == "__main__":
    asyncio.run(main())