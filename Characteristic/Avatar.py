#!/usr/bin/env python3
from datetime import datetime
from typing import Dict, List, Literal
from pydantic import BaseModel, Field


def spawn_by_percentage(OptionA: str, OptionB: str, percentageA: str) -> str:
    p = float(percentageA.strip("%")) / 100
    if not 0 <= p <= 1:
        raise ValueError("Percentage must be 0-100%")

    keyword = f"{OptionA}/{OptionB}"

    if p < 0.05:
        return f"{keyword}: extremely {OptionB} ({100-p*100:.1f}%)"
    elif p < 0.15:
        return f"{keyword}: strongly {OptionB} ({100-p*100:.1f}%)"
    elif p < 0.35:
        return f"{keyword}: moderately {OptionB} ({100-p*100:.1f}%)"
    elif p < 0.45:
        return f"{keyword}: slightly {OptionB}-leaning ({100-p*100:.1f}%)"
    elif p <= 0.55:
        return f"{keyword}: ideally balanced"
    elif p <= 0.65:
        return f"{keyword}: slightly {OptionA}-leaning ({p*100:.1f}%)"
    elif p <= 0.85:
        return f"{keyword}: moderately {OptionA} ({p*100:.1f}%)"
    elif p <= 0.95:
        return f"{keyword}: strongly {OptionA} ({p*100:.1f}%)"
    else:
        return f"{keyword}: extremely {OptionA} ({p*100:.1f}%)"


class MBTIScores(BaseModel):
    Extraversion_Introversion: str = Field(..., pattern=r"^\d{1,3}(\.\d+)?%$")
    Sensing_Intuition: str = Field(..., pattern=r"^\d{1,3}(\.\d+)?%$")
    Thinking_Feeling: str = Field(..., pattern=r"^\d{1,3}(\.\d+)?%$")
    Judging_Perceiving: str = Field(..., pattern=r"^\d{1,3}(\.\d+)?%$")
    Conclusion: str

    def get_summary(self, layer: int = 0) -> str:
        summary = (
            "\t" * layer
            + spawn_by_percentage(
                "Extraversion", "Introversion", self.Extraversion_Introversion
            )
            + "\n"
        )
        summary += (
            "\t" * layer
            + spawn_by_percentage("Sensing", "Intuition", self.Sensing_Intuition)
            + "\n"
        )
        summary += (
            "\t" * layer
            + spawn_by_percentage("Thinking", "Feeling", self.Thinking_Feeling)
            + "\n"
        )
        summary += (
            "\t" * layer
            + spawn_by_percentage("Judging", "Perceiving", self.Judging_Perceiving)
            + "\n"
        )
        summary += "\t" * layer + f"Conclusion: {self.Conclusion}\n"
        return summary


class PolitiScales(BaseModel):
    Federal_Unitary: str = Field(..., pattern=r"^\d{1,3}(\.\d+)?%$")
    Democracy_Authority: str = Field(..., pattern=r"^\d{1,3}(\.\d+)?%$")
    Globalist_Isolationist: str = Field(..., pattern=r"^\d{1,3}(\.\d+)?%$")
    Militarist_Pacifist: str = Field(..., pattern=r"^\d{1,3}(\.\d+)?%$")
    Security_Freedom: str = Field(..., pattern=r"^\d{1,3}(\.\d+)?%$")
    Equality_Markets: str = Field(..., pattern=r"^\d{1,3}(\.\d+)?%$")
    Secular_Religious: str = Field(..., pattern=r"^\d{1,3}(\.\d+)?%$")
    Progress_Tradition: str = Field(..., pattern=r"^\d{1,3}(\.\d+)?%$")
    Assimilationist_Multiculturalist: str = Field(..., pattern=r"^\d{1,3}(\.\d+)?%$")

    def get_summary(self, layer: int = 0) -> str:
        summary = (
            "\t" * layer
            + spawn_by_percentage("Federal", "Unitary", self.Federal_Unitary)
            + "\n"
        )
        summary += (
            "\t" * layer
            + spawn_by_percentage("Democracy", "Authority", self.Democracy_Authority)
            + "\n"
        )
        summary += (
            "\t" * layer
            + spawn_by_percentage(
                "Globalist", "Isolationist", self.Globalist_Isolationist
            )
            + "\n"
        )
        summary += (
            "\t" * layer
            + spawn_by_percentage("Militarist", "Pacifist", self.Militarist_Pacifist)
            + "\n"
        )
        summary += (
            "\t" * layer
            + spawn_by_percentage("Security", "Freedom", self.Security_Freedom)
            + "\n"
        )
        summary += (
            "\t" * layer
            + spawn_by_percentage("Equality", "Markets", self.Equality_Markets)
            + "\n"
        )
        summary += (
            "\t" * layer
            + spawn_by_percentage("Secular", "Religious", self.Secular_Religious)
            + "\n"
        )
        summary += (
            "\t" * layer
            + spawn_by_percentage("Progress", "Tradition", self.Progress_Tradition)
            + "\n"
        )
        summary += (
            "\t" * layer
            + spawn_by_percentage(
                "Assimilationist",
                "Multiculturalist",
                self.Assimilationist_Multiculturalist,
            )
            + "\n"
        )
        return summary


class Personalities(BaseModel):
    MBTI: MBTIScores
    PolitiScales: PolitiScales

    def get_summary(self, layer: int = 0) -> str:
        summary = "\t" * layer + "MBTI:\n"
        summary += self.MBTI.get_summary(layer + 1)
        summary += "\t" * layer + "Political Scales:\n"
        summary += self.PolitiScales.get_summary(layer + 1)
        return summary


class SignificantCharacter(BaseModel):
    Name: str
    Gender: Literal["Male", "Female"]
    Birthplace: str
    Relationship: str
    Events: List[str]

    def get_summary(self, layer: int = 0) -> str:
        summary = "\t" * layer + f"Name: {self.Name}\n"
        summary += "\t" * layer + f"Gender: {self.Gender}\n"
        summary += "\t" * layer + f"Birthplace: {self.Birthplace}\n"
        summary += "\t" * layer + f"Relationship: {self.Relationship}\n"
        summary += (
            "\t" * layer
            + f"Events: {'\n' + '\t'*(layer+1) + ('\n' + '\t'*(layer+1)).join(self.Events)}\n"
        )
        return summary


class CharacterModel(BaseModel):
    Name: str
    Born: str = Field(..., pattern=r"^\d{1,2}/\d{1,2}/\d{4}$")
    Gender: Literal["Male", "Female"]
    Birthplace: str
    Backstory: str
    Traits: List[str]
    Personalities: Personalities
    Significant_Events: List[str]
    Interests: List[str]
    Significant_Characters: List[SignificantCharacter]

    def get_summary(self, layer: int = 0) -> str:
        summary = "\t" * layer + f"Name: {self.Name}\n"
        summary += "\t" * layer + f"Born: {self.Born}\n"
        summary += "\t" * layer + f"Gender: {self.Gender}\n"
        summary += "\t" * layer + f"Birthplace: {self.Birthplace}\n"
        summary += "\t" * layer + f"Backstory: {self.Backstory}\n"
        summary += (
            "\t" * layer
            + f"Traits: {'\n' + '\t'*(layer+1) + ('\n' + '\t'*(layer+1)).join(self.Traits)}\n"
        )
        summary += (
            "\t" * layer
            + f"Personalities: \n{self.Personalities.get_summary(layer + 1)}\n"
        )
        summary += (
            "\t" * layer
            + f"Significant Events: {'\n' + '\t'*(layer+1) + ('\n' + '\t'*(layer+1)).join(self.Significant_Events)}\n"
        )
        summary += (
            "\t" * layer
            + f"Interests: {'\n' + '\t'*(layer+1) + ('\n' + '\t'*(layer+1)).join(self.Interests)}\n"
        )
        summary += (
            "\t" * layer
            + f"Significant Characters: {'\n' + '\n'.join([char.get_summary(layer + 1) for char in self.Significant_Characters])}\n"
        )
        return summary


class Avatar:
    def __init__(self, character_data: Dict):
        try:
            self.validated = CharacterModel(**character_data)
        except ValueError as e:
            raise ValueError(f"Characteristic-Avatar.py: Invalid character data: {e}")

        self.name: str = self.validated.Name
        self.born: datetime = datetime.strptime(self.validated.Born, "%m/%d/%Y")
        self.gender: Literal["Male", "Female"] = self.validated.Gender
        self.birthplace: str = self.validated.Birthplace
        self.backstory: str = self.validated.Backstory
        self.traits: List[str] = self.validated.Traits
        self.personalities: dict = self.validated.Personalities.model_dump()
        self.Significant_Events: List[str] = self.validated.Significant_Events
        self.Interests: List[str] = self.validated.Interests
        self.Significant_Characters: List[SignificantCharacter] = (
            self.validated.Significant_Characters
        )

    def get_summary(self) -> str:
        return self.validated.get_summary()
