from pydantic import BaseModel, Field

class AdGenerationRequest(BaseModel):
    platform: str = Field(..., description="The platform where the ad will be displayed (e.g., Instagram, Facebook, LinkedIn)")
    product: str = Field(..., description="The product or service the ad is promoting")
    tone: str = Field(..., description="The tone or style of the ad (e.g., casual, professional, witty)")
    goal: str = Field(..., description="The primary goal of the ad (e.g., conversions, awareness, traffic)")
    description: str = Field(..., description="A brief description of the product or service")