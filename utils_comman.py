__author__ = "Nitin Patil"


#-----------------------------------------------------------------------------------
PATH = "./data"
MAPBOX_TOKEN= "pk.eyJ1IjoicGF0aWxuaXRpbjIzIiwiYSI6ImNrN2JoNTB6ODA0NDIzbnB2ZzI4MTdsYnMifQ.Sw8udcIf539mektKpvgRYw"

COLOR_MAP = {
            #"Brown": "rgb(87, 22, 22)",
            "Brown": "rgb(160,82,45)",
            "Sienna": "rgb(160,82,45)", # For Total cases
            "Black": "rgb(0, 0, 0)",
            "Red": "rgb(216, 0, 0)",
            
            "Green": "rgb(0, 128, 0)",
            
            "ForestGreen":"rgb(34,139,34)",
            "Light_Red": "rgb(196, 0, 0)",
            "Light_Green": "rgb(0, 120, 0)",
            "Blue": "rgb(0, 0, 255)", 
            #"Orange": "rgb(255, 115, 0)",
            #"Orange": "rgb(244,164,96)",
            "Orange":	"rgb(255,140,0)",
            "White": "rgb(255, 255, 255)",
            "SandyBrown": "rgb(244,164,96)", # For active
            "DarkOrange":	"rgb(255,140,0)", # For active
            "Salmon":"rgb(250,128,114)", # For Deaths
            "LightGreen":"rgb(144,238,144)"}

TYPE_TO_COLOR={
    "Total":"Brown",
    "Recovered":"Green",
    "Deaths":"Red",
    "Active":"Orange",
    "Default":"Red"
}

TIMEOUT = 60
LINE_WIDTH = 4

