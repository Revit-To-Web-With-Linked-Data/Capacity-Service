import fluids
from pyfluids import Fluid, PureFluids, Input
import math
import uuid
import numpy as np

def tees(graph): 
  ###Extracting data at component level and send it to fluid component
  distributionComponents ={
  "@graph" : [ ],
   "@context": {

        "fpo:hasValue": {
            "@id": "https://w3id.org/fpo#hasValue",
            "@type": "http://www.w3.org/2001/XMLSchema#double"
        },
        "hasPressureDrop": {
            "@id": "https://w3id.org/fpo#hasPressureDrop",
            "@type": "@id"
        },
        "ex": "https://example.com/ex#",
        "fso": "https://w3id.org/fso#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "fpo": "https://w3id.org/fpo#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "inst": "https://example.com/inst#"
    }

  #####################TEE COMPONENTS 
  }   
  TeeComponents ={
   "@graph":[
      
   ]
  }

  for item1 in graph['@graph']:
    portArray =[]
    if "@type" in item1:
      id=item1["@id"]
      directionVectorArray = []
      for port in item1["hasPort"]:
        for item2 in graph['@graph']:
          if "@id" in item2:
            if item2["@id"] == port:
              item2["hasFlowDirectionVectorZ"] =item2["hasFlowDirectionVectorZ"][1:]
              item2["hasFlowDirectionVectorZ"] =item2["hasFlowDirectionVectorZ"][:-1]

              item2["hasFlowDirectionVectorZ"] =item2["hasFlowDirectionVectorZ"].split(", ")
              directionVectorArray = []
              for directionVector in item2["hasFlowDirectionVectorZ"]:
                directionVectorArray.append(float(directionVector))
              flowDirection = item2["hasFlowDirection"]
              flowType = item2["hasFlowType"]
              temperature = item2["fpo:hasTemperature"]
              velocity = item2["fpo:hasVelocity"]
              flowRate = item2["fpo:hasFlowRate"]

              if "fpo:hasOuterDiameter" in item2:
                outerDiameter =item2["fpo:hasOuterDiameter"]
                crossSectionalArea =item2["fpo:hasCrossSectionalArea"]

                portArray.append({
                "@id": item2["@id"],
                "hasFlowDirection": flowDirection,
                "hasFlowType": flowType,
                "fpo:hasTemperature": temperature,
                "fpo:hasVelocity": velocity,
                "hasFlowDirectionVectorZ": directionVectorArray,
                "fpo:hasFlowRate": flowRate,
                "fpo:hasOuterDiameter": outerDiameter,
                "fpo:hasCrossSectionalArea": crossSectionalArea

              })

              if "fpo:hasWidth" in item2:
                width =item2["fpo:hasWidth"]
                height =item2["fpo:hasHeight"]
                crossSectionalArea =item2["fpo:hasCrossSectionalArea"]

                portArray.append({
                "@id": item2["@id"],
                "hasFlowDirection": flowDirection,
                "hasFlowType": flowType,
                "fpo:hasTemperature": temperature,
                "fpo:hasVelocity": velocity,
                "hasFlowDirectionVectorZ": directionVectorArray,
                "fpo:hasFlowRate": flowRate,
                "fpo:hasWidth": width,
                "fpo:hasHeight": height,
                "fpo:hasCrossSectionalArea": crossSectionalArea
                })


             
              

      Tee ={"@id": item1["@id"], "hasPort":portArray, "RevitID" :item1["RevitID"]}
      TeeComponents["@graph"].append(Tee)

  # Calculate pressure drop for each Tee and add it to object
  pressureDrops = TeeIdentifier(TeeComponents)
  for i in pressureDrops:
    distributionComponents["@graph"].append(i)
          
  return distributionComponents


def pipes(graph): 
  ###Extracting data at component level and send it to fluid component
  distributionComponents ={
  "@graph" : [ ],
   "@context": {

        "fpo:hasValue": {
            "@id": "https://w3id.org/fpo#hasValue",
            "@type": "http://www.w3.org/2001/XMLSchema#double"
        },
        "hasPressureDrop": {
            "@id": "https://w3id.org/fpo#hasPressureDrop",
            "@type": "@id"
        },
        "ex": "https://example.com/ex#",
        "fso": "https://w3id.org/fso#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "fpo": "https://w3id.org/fpo#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "inst": "https://example.com/inst#"
    }

  #####################TEE COMPONENTS 
  }   

  for item1 in graph['@graph']:
    # print(item1['@type'])
  #Calculate pressure drop for each pipe and duct and add it to object
    if (item1['@type'] =='fso:Pipe' or item1['@type'] =='fso:Duct'):
        result=pipeFluids(item1["@id"], item1["fpo:hasTemperature"], item1["hasFlowType"], item1["fpo:hasLength"], item1["fpo:hasRoughness"], item1["fpo:hasVelocity"], item1["fpo:hasOuterDiameter"])

        distributionComponents["@graph"].extend(result)
  
  # Calculate pressure drop for each elbow and add it to object
    if (item1['@type'] =='fso:Elbow'):
        result=ElbowFluids(item1["@id"], item1["fpo:hasTemperature"], item1["hasFlowType"], item1["fpo:hasAngle"], item1["fpo:hasRoughness"], item1["fpo:hasVelocity"], item1["fpo:hasOuterDiameter"])

        distributionComponents["@graph"].extend(result)

  #Calculate pressure drop for each transition and add it to object
    if (item1['@type'] =='fso:Transition'):
        result=TransitionFluids(item1["@id"], item1["fpo:hasTemperature"], item1["hasFlowType"], item1["fpo:hasVelocity"], item1["fpo:hasOuterDiameter"],item1["fpo:hasInnerDiameter"], item1["hasSystem"], item1["fpo:hasLength"])

        distributionComponents["@graph"].extend(result)
        
  return distributionComponents




###Based on the flow direction vector we identify each Tee type and send it to the pressure calculator. We also return the result of the pressure drop and adds it to component. 
def TeeIdentifier (Tees):
  pressureDrops =[]
  for component in Tees["@graph"]: 
    inletArray =[]
    outletArray=[]
    for port in component["hasPort"]:
      directionVectorArray = []
      #print(port["hasFlowDirection"])
      if port["hasFlowDirection"] == "In":
        inletArray.append(port["hasFlowDirectionVectorZ"])
      if port["hasFlowDirection"] == "Out":
        outletArray.append(port["hasFlowDirectionVectorZ"])
    
    # print("inletArray:", len(inletArray))
    # print("outletAray:", len(outletArray))
    if len(inletArray) == 2:
      #IF 2 Out flowDirections then we have either fordeling or afgrening
      z11 = inletArray[0][0]
      z12 = inletArray[0][1]
      z13 = inletArray[0][2]
      z21 = inletArray[1][0]
      z22 = inletArray[1][1]
      z23 = inletArray[1][2]
      z1 =z11 + z21
      z2 =z12 + z22
      z3 =z13 + z23
      if z1 ==0 and z2 ==0 and z3 ==0:
        if port["hasFlowType"] =="Water":
          if component["@id"] == "inst:98e9914f-25c6-4c43-a0fb-912eba89c13d-0019da5c":
            print("Sammenlob Water")
          sammenlobWaterPressureDrops = SammenlobWaterPressureCalculation(component)
          for i in sammenlobWaterPressureDrops:
            pressureDrops.append(i)        
        else:
          if component["@id"] == "inst:98e9914f-25c6-4c43-a0fb-912eba89c13d-0019da5c":
            print("Sammenlob Air")
          sammenlobAirPressureDrops = SammenlobAirPressureCalculation(component)
          for i in sammenlobAirPressureDrops:
            pressureDrops.append(i)        
      else:
        if port["hasFlowType"] =="Water":
          if component["@id"] == "inst:98e9914f-25c6-4c43-a0fb-912eba89c13d-0019da5c":
            print("Tillob Water")
          tillobWaterPressureDrops = TillobWaterPressureCalculation(component)
          for i in tillobWaterPressureDrops:
            pressureDrops.append(i)
        if port["hasFlowType"] =="Air":
          if component["@id"] == "inst:98e9914f-25c6-4c43-a0fb-912eba89c13d-0019da5c":
            print("Tillob Air")
          tillobAirPressureDrops = TillobAirPressureCalculation(component)
          for i in tillobAirPressureDrops:
            pressureDrops.append(i)



    if len(outletArray) == 2:
      #IF 2 In flowDirections then we have either sammenløb or tilløb
      z11 = outletArray[0][0]
      z12 = outletArray[0][1]
      z13 = outletArray[0][2]
      z21 = outletArray[1][0]
      z22 = outletArray[1][1]
      z23 = outletArray[1][2]
      z1 =z11 + z21
      z2 =z12 + z22
      z3 =z13 + z23
      if z1 ==0 and z2 ==0 and z3 ==0:
        if port["hasFlowType"] =="Water":
          if component["@id"] == "inst:98e9914f-25c6-4c43-a0fb-912eba89c13d-0019da5c":
            print("Fordeling Water")
          fordelingWaterPressureDrops = FordelingWaterPressureCalculation(component)
          for i in fordelingWaterPressureDrops:
            pressureDrops.append(i)
        else:
          if component["@id"] == "inst:98e9914f-25c6-4c43-a0fb-912eba89c13d-0019da5c":
            print("Fordeling Air")
          fordelingAirPressureDrops= FordelingAirPressureCalculation(component)
          for i in fordelingAirPressureDrops:
            pressureDrops.append(i)          
      else:
        if port["hasFlowType"] =="Water":
          if component["@id"] == "inst:98e9914f-25c6-4c43-a0fb-912eba89c13d-0019da5c":
            print("Afgrening Water")
          afgreningWaterPressureDrops = AfgreningWaterPressureCalculation(component)
          for i in afgreningWaterPressureDrops:
              pressureDrops.append(i)
        if port["hasFlowType"] =="Air":
          if component["@id"] == "inst:98e9914f-25c6-4c43-a0fb-912eba89c13d-0019da5c":
            print("Afgrening Air") 
          afgreningAirPressureDrops = AfgreningAirPressureCalculation(component)
          for i in afgreningAirPressureDrops:
              pressureDrops.append(i)

  return pressureDrops


def SammenlobAirPressureCalculation(component):
  inletPort ={}
  outletPort ={}
  
  for port in component["hasPort"]:
    if port["hasFlowDirection"] == "Out":
      outletPort = port
      SammenlobArray = []
      pressureDropMaxArray = []
      for newPort in component["hasPort"]:
        if newPort["hasFlowDirection"] == "In":
          inletPort = newPort

          q = outletPort["fpo:hasFlowRate"]
          q2= inletPort["fpo:hasFlowRate"]
          v2 = inletPort["fpo:hasVelocity"]
          
          xp = [0.1, 0.2 , 0.3, 0.4 , 0.5, 0.6, 0.7, 0.8, 0.9]
          fp = [54.54, 11.83, 4.60, 2.47, 1.57, 1.13, 0.95, 0.08, 1.24]
          theta = np.interp(q2/q, xp, fp)

          fluidTemperature = outletPort["fpo:hasTemperature"] # *C
          fluid_vapour = Fluid(PureFluids.Air)
          fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature)) 
          density = fluid_vapour.density #kg/m3
          pressureDropValue = 0.5*density*math.pow(v2,2)*theta

          pressureDropMaxArray.append(pressureDropValue)

      #Anvender kun max værdi for inlet pressure og lægger det på outletport. Gjort bevidst pga. simplificering  
      pressureDropID = "inst:"+str(uuid.uuid4())
      portData = {
      "@id" : outletPort["@id"],
      "hasPressureDrop" : pressureDropID
      }
      pressureDropData={ 
        "@id" : pressureDropID,
      "fpo:hasValue" : max(pressureDropMaxArray)
      }
      SammenlobArray.append(portData)
      SammenlobArray.append(pressureDropData)

      return SammenlobArray



def SammenlobWaterPressureCalculation(component):
  inletPort ={}
  outletPort ={}
  
  for port in component["hasPort"]:
    if port["hasFlowDirection"] == "Out":
      outletPort = port
      SammenlobArray = []
      pressureDropMaxArray = []
      for newPort in component["hasPort"]:
        if newPort["hasFlowDirection"] == "In":
          inletPort = newPort
          z11 = inletPort["hasFlowDirectionVectorZ"][0]
          z12 = inletPort["hasFlowDirectionVectorZ"][1]
          z13 = inletPort["hasFlowDirectionVectorZ"][2]
          z21 = outletPort["hasFlowDirectionVectorZ"][0]
          z22 = outletPort["hasFlowDirectionVectorZ"][1]
          z23 = outletPort["hasFlowDirectionVectorZ"][2]
          z1 =z11 + z21
          z2 =z12 + z22
          z3 =z13 + z23

          q = outletPort["fpo:hasFlowRate"]
          q2= inletPort["fpo:hasFlowRate"]
          d = outletPort["fpo:hasOuterDiameter"]
          d2= inletPort["fpo:hasOuterDiameter"]
          v2 = inletPort["fpo:hasVelocity"]
          
          if round(d2/d,1) <= 0.5:
            xp = [0.3, 0.5, 0.7]
            fp = [5, 1.3, 1]
            theta = np.interp(q2/q, xp, fp)
          
          if round(d2/d,1) < 0.5 and round(d2/d,1) <= 0.7:
            xp = [0.3, 0.5, 0.7]
            fp = [7, 2, 1.3]
            theta = np.interp(q2/q, xp, fp)

          if round(d2/d,1) > 0.7 and round(d2/d,1) <= 0.8:
            xp = [0.3, 0.5, 0.7]
            fp = [9, 3, 1.3]
            theta = np.interp(q2/q, xp, fp)

          if round(d2/d,1) > 0.8 and round(d2/d,1) <= 1:
            xp = [0.3, 0.5, 0.7]
            fp = [9, 3, 1.8]
            theta = np.interp(q2/q, xp, fp)

          if round(d2/d,1) > 1:
            xp = [0.3, 0.5, 0.7]
            fp = [15, 5, 3]
            theta = np.interp(q2/q, xp, fp)

          fluidTemperature = outletPort["fpo:hasTemperature"] # *C
          fluid_vapour = Fluid(PureFluids.Water)
          fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature)) 
          density = fluid_vapour.density #kg/m3
          pressureDropValue = 0.5*density*math.pow(v2,2)*theta

          pressureDropMaxArray.append(pressureDropValue)

      #Anvender kun max værdi for inlet pressure og lægger det på outletport. Gjort bevidst pga. simplificering  
      pressureDropID = "inst:"+str(uuid.uuid4())
      portData = {
      "@id" : outletPort["@id"],
      "hasPressureDrop" : pressureDropID
      }
      pressureDropData={ 
        "@id" : pressureDropID,
      "fpo:hasValue" : max(pressureDropMaxArray)
      }
      SammenlobArray.append(portData)
      SammenlobArray.append(pressureDropData)

      return SammenlobArray
def TillobAirPressureCalculation(component):
  inletPort ={}
  outletPort ={}
  
  for port in component["hasPort"]:
    if port["hasFlowDirection"] == "Out":
      outletPort = port
      TillobArray = []
      pressureDropMaxArray = []
      for newPort in component["hasPort"]:
        if newPort["hasFlowDirection"] == "In":
          inletPort = newPort
          z11 = inletPort["hasFlowDirectionVectorZ"][0]
          z12 = inletPort["hasFlowDirectionVectorZ"][1]
          z13 = inletPort["hasFlowDirectionVectorZ"][2]
          z21 = outletPort["hasFlowDirectionVectorZ"][0]
          z22 = outletPort["hasFlowDirectionVectorZ"][1]
          z23 = outletPort["hasFlowDirectionVectorZ"][2]
          z1 =z11 + z21
          z2 =z12 + z22
          z3 =z13 + z23

          #PARRALEL PORT
          if z1 ==0 and z2 ==0 and z3 ==0:
            q = outletPort["fpo:hasFlowRate"]
            q1= inletPort["fpo:hasFlowRate"]
            v1 = inletPort["fpo:hasVelocity"]
            
            xp = [0.1, 0.2 , 0.3, 0.4 , 0.5, 0.6, 0.7, 0.8, 0.9]
            fp = [237.9, 37.35, 12.88, 5.92, 3.08, 1.68 ,0.88 ,0.39 ,0.07]
            theta = np.interp(q1/q, xp, fp)

            fluidTemperature = outletPort["fpo:hasTemperature"] # *C
            fluid_vapour = Fluid(PureFluids.Air)
            fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature)) 
            density = fluid_vapour.density #kg/m3
            pressureDropValue = 0.5*density*math.pow(v1,2)*theta

            pressureDropMaxArray.append(pressureDropValue)
           
          #ORTHOGONAL PORT
          if z1 !=0 or z2 !=0 or z3 !=0:
            q = outletPort["fpo:hasFlowRate"]
            q2= inletPort["fpo:hasFlowRate"]
            v2 = inletPort["fpo:hasVelocity"]
            
            xp = [0.1, 0.2 , 0.3, 0.4 , 0.5, 0.6, 0.7, 0.8, 0.9]
            fp = [-39.19, -2.55, 1.76, 2.43, 2.35, 2.12, 1.9, 1.81, 2.3]
            theta = np.interp(q2/q, xp, fp)

            fluidTemperature = outletPort["fpo:hasTemperature"] # *C
            fluid_vapour = Fluid(PureFluids.Air)
            fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature)) 
            density = fluid_vapour.density #kg/m3
            pressureDropValue = 0.5*density*math.pow(v2,2)*theta

            pressureDropMaxArray.append(pressureDropValue)

      #Anvender kun max værdi for inlet pressure og lægger det på outletport. Gjort bevidst pga. simplificering  
      pressureDropID = "inst:"+str(uuid.uuid4())
      portData = {
      "@id" : outletPort["@id"],
      "hasPressureDrop" : pressureDropID
      }
      pressureDropData={ 
        "@id" : pressureDropID,
      "fpo:hasValue" : max(pressureDropMaxArray)
      }
      TillobArray.append(portData)
      TillobArray.append(pressureDropData)

      return TillobArray
def TillobWaterPressureCalculation(component):
  inletPort ={}
  outletPort ={}
  
  for port in component["hasPort"]:
    if port["hasFlowDirection"] == "Out":
      outletPort = port
      TillobArray = []
      pressureDropMaxArray = []
      for newPort in component["hasPort"]:
        if newPort["hasFlowDirection"] == "In":
          inletPort = newPort
          z11 = inletPort["hasFlowDirectionVectorZ"][0]
          z12 = inletPort["hasFlowDirectionVectorZ"][1]
          z13 = inletPort["hasFlowDirectionVectorZ"][2]
          z21 = outletPort["hasFlowDirectionVectorZ"][0]
          z22 = outletPort["hasFlowDirectionVectorZ"][1]
          z23 = outletPort["hasFlowDirectionVectorZ"][2]
          z1 =z11 + z21
          z2 =z12 + z22
          z3 =z13 + z23

          #PARRALEL PORT
          if z1 ==0 and z2 ==0 and z3 ==0:
            q = outletPort["fpo:hasFlowRate"]
            q1= inletPort["fpo:hasFlowRate"]
            d = outletPort["fpo:hasOuterDiameter"]
            d1= inletPort["fpo:hasOuterDiameter"]
            v1 = inletPort["fpo:hasVelocity"]
            
            if d1/d < 1:
              xp = [0.6, 0.8, 1]
              fp = [0.8, 0.3, 0]
              theta = np.interp(q1/q, xp, fp)
            
            if d1/d == 1:
              xp = [0.6, 0.8, 1]
              fp = [1.5, 0.5, 0]
              theta = np.interp(q1/q, xp, fp)

            fluidTemperature = outletPort["fpo:hasTemperature"] # *C
            fluid_vapour = Fluid(PureFluids.Water)
            fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature)) 
            density = fluid_vapour.density #kg/m3
            pressureDropValue = 0.5*density*math.pow(v1,2)*theta

            pressureDropMaxArray.append(pressureDropValue)
           
          #ORTHOGONAL PORT
          if z1 !=0 or z2 !=0 or z3 !=0:
            q = outletPort["fpo:hasFlowRate"]
            q2= inletPort["fpo:hasFlowRate"]
            d = outletPort["fpo:hasOuterDiameter"]
            d2= inletPort["fpo:hasOuterDiameter"]
            v2 = inletPort["fpo:hasVelocity"]
            
            if round(d2/d,1) <= 0.3:
              xp = [0.1, 0.2, 0.3, 0.4, 0.5]
              fp = [0.5, 1, 1, 1, 1]
              theta = np.interp(q2/q, xp, fp)
            
            if round(d2/d,1) < 0.3 and round(d2/d,1) <= 0.4:
              xp = [0.1, 0.2, 0.3, 0.4, 0.5]
              fp = [0, 1, 1.3, 1, 1]
              theta = np.interp(q2/q, xp, fp)

            if round(d2/d,1) > 0.4 and round(d2/d,1) <= 0.5:
              xp = [0.1, 0.2, 0.3, 0.4 , 0.5]
              fp = [-2, 0.5, 1 ,1 , 1]
              theta = np.interp(q2/q, xp, fp)

            if round(d2/d,1) > 0.5 and round(d2/d,1) <= 0.7:
              xp = [0.1, 0.2, 0.3, 0.4 , 0.5]
              fp = [-7, 0, 1 ,1.3 , 1.5]
              theta = np.interp(q2/q, xp, fp)

            if round(d2/d,1) >= 1:
              xp = [0.1, 0.2, 0.3, 0.4 , 0.5]
              fp = [-2, -2, -2 ,1.5 , 2]
              theta = np.interp(q2/q, xp, fp)

            fluidTemperature = outletPort["fpo:hasTemperature"] # *C
            fluid_vapour = Fluid(PureFluids.Water)
            fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature)) 
            density = fluid_vapour.density #kg/m3
            pressureDropValue = 0.5*density*math.pow(v2,2)*theta

            pressureDropMaxArray.append(pressureDropValue)

      #Anvender kun max værdi for inlet pressure og lægger det på outletport. Gjort bevidst pga. simplificering  
      pressureDropID = "inst:"+str(uuid.uuid4())
      portData = {
      "@id" : outletPort["@id"],
      "hasPressureDrop" : pressureDropID
      }
      pressureDropData={ 
        "@id" : pressureDropID,
      "fpo:hasValue" : max(pressureDropMaxArray)
      }
      TillobArray.append(portData)
      TillobArray.append(pressureDropData)

      return TillobArray
def FordelingAirPressureCalculation(component):
  inletPort ={}
  outletPort ={}
  for port in component["hasPort"]:
    if port["hasFlowDirection"] == "In":
      inletPort = port
      FordelingArray = []

      for newPort in component["hasPort"]:
        if newPort["hasFlowDirection"] == "Out":
          outletPort = newPort
          v = inletPort["fpo:hasVelocity"]
          v2 = outletPort["fpo:hasVelocity"]

          #Linnear interpolating theta
          xp = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
          fp = [22.50, 5.00, 2.08, 1.25, 1.10, 0.83, 0.61, 0.47, 0.37]
          theta = np.interp(v2/v, xp, fp)    
          
          fluidTemperature = outletPort["fpo:hasTemperature"] # *C
          fluid_vapour = Fluid(PureFluids.Air)
          fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature)) 
          density = fluid_vapour.density #kg/m3
          pressureDropValue =0.5*density*math.pow(v2,2)*theta

          pressureDropID = "inst:"+str(uuid.uuid4())
          portData = {
          "@id" : outletPort["@id"],
          "hasPressureDrop" : pressureDropID
          }
          pressureDropData={ 
            "@id" : pressureDropID,
          "fpo:hasValue" : pressureDropValue
          }
          FordelingArray.append(portData)
          FordelingArray.append(pressureDropData)
      return FordelingArray
def FordelingWaterPressureCalculation(component):
  inletPort ={}
  outletPort ={}
  for port in component["hasPort"]:
    if port["hasFlowDirection"] == "In":
      inletPort = port
      FordelingArray = []

      for newPort in component["hasPort"]:
        if newPort["hasFlowDirection"] == "Out":
          outletPort = newPort
          v = inletPort["fpo:hasVelocity"]
          v2 = outletPort["fpo:hasVelocity"]

          #Linnear interpolating theta
          xp = [0.6, 1, 1.5, 2]
          fp = [3, 1.3, 0.8 , 0.5]
          theta = np.interp(v2/v, xp, fp)    
          
          fluidTemperature = outletPort["fpo:hasTemperature"] # *C
          fluid_vapour = Fluid(PureFluids.Water)
          fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature)) 
          density = fluid_vapour.density #kg/m3
          pressureDropValue =0.5*density*math.pow(v2,2)*theta

          pressureDropID = "inst:"+str(uuid.uuid4())
          portData = {
          "@id" : outletPort["@id"],
          "hasPressureDrop" : pressureDropID
          }
          pressureDropData={ 
            "@id" : pressureDropID,
          "fpo:hasValue" : pressureDropValue
          }
          FordelingArray.append(portData)
          FordelingArray.append(pressureDropData)
      return FordelingArray
def AfgreningAirPressureCalculation(component):
  inletPort ={}
  outletPort ={}
  for port in component["hasPort"]:
    if port["hasFlowDirection"] == "In":
      inletPort = port
      AfgreningArray =[]

      for newPort in component["hasPort"]:
        if newPort["hasFlowDirection"] == "Out":
          outletPort = newPort
          z11 = inletPort["hasFlowDirectionVectorZ"][0]
          z12 = inletPort["hasFlowDirectionVectorZ"][1]
          z13 = inletPort["hasFlowDirectionVectorZ"][2]
          z21 = outletPort["hasFlowDirectionVectorZ"][0]
          z22 = outletPort["hasFlowDirectionVectorZ"][1]
          z23 = outletPort["hasFlowDirectionVectorZ"][2]
          z1 =z11 + z21
          z2 =z12 + z22
          z3 =z13 + z23

          if z1 ==0 and z2 ==0 and z3 ==0:
            q = inletPort["fpo:hasFlowRate"]
            q1 = outletPort["fpo:hasFlowRate"]
            A = inletPort["fpo:hasCrossSectionalArea"]
            A1 = outletPort["fpo:hasCrossSectionalArea"]
            v1 = outletPort["fpo:hasVelocity"]           
           
            #Linnear interpolating theta
            if round(A1/A,1) <= 0.1:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [1.2,4.1,8.99,15.89,24.8,35.73,48.67,63.63,80.60]
              theta = np.interp(q1/q, xp, fp)
            
            if round(A1/A,1) > 0.1 and round(A1/A,1) <= 0.2:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [0.62,1.2,2.4,4.1,6.29,8.99,12.19,15.89,20.10]
              theta = np.interp(q1/q, xp, fp)

            if round(A1/A,1) > 0.2 and round(A1/A,1) <= 0.3:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [0.8,0.72,1.2,1.94,2.91,4.1,5.51,7.13,8.99]
              theta = np.interp(q1/q, xp, fp)

            if round(A1/A,1) > 0.3 and round(A1/A,1) <= 0.4:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [1.28,0.62,0.81,1.2,1.74,2.4,3.19,4.10,5.13]
              theta = np.interp(q1/q, xp, fp)

            if round(A1/A,1) > 0.4 and round(A1/A,1) <= 0.5:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [1.99, 0.66, 0.66, 0.88, 1.20, 1.62, 2.12, 2.70, 3.36]
              theta = np.interp(q1/q, xp, fp)

            if round(A1/A,1) > 0.5 and round(A1/A,1) <= 0.6:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [2.92, 0.80, 0.62, 0.72, 0.92, 1.20, 1.55, 1.94, 2.40]
              theta = np.interp(q1/q, xp, fp)

            if round(A1/A,1) > 0.6 and round(A1/A,1) <= 0.7:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [4.07, 1.01, 0.64, 0.64, 0.77, 0.96, 1.20, 1.49, 1.83]
              theta = np.interp(q1/q, xp, fp)
              
            if round(A1/A,1) > 0.7 and round(A1/A,1) <= 0.8:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [5.44, 1.28, 0.70, 0.62, 0.68, 0.81, 0.99, 1.20, 1.46]
              theta = np.interp(q1/q, xp, fp)
              
            if round(A1/A,1) >= 0.9:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [7.02, 1.60, 0.80, 0.63, 0.63, 0.72, 0.85, 1.01, 1.20]
              theta = np.interp(q1/q, xp, fp)

            fluidTemperature = outletPort["fpo:hasTemperature"] # *C
            fluid_vapour = Fluid(PureFluids.Air)
            fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature)) 
            density = fluid_vapour.density #kg/m3
            pressureDropValue =0.5*density*math.pow(v1,2)*theta

            pressureDropID = "inst:"+str(uuid.uuid4())
            portData = {
            "@id" : outletPort["@id"],
            "hasPressureDrop" : pressureDropID
            }
            pressureDropData={ 
              "@id" : pressureDropID,
            "fpo:hasValue" : pressureDropValue
            }
            AfgreningArray.append(portData)
            AfgreningArray.append(pressureDropData)

            
          if z1 !=0 or z2 !=0 or z3 !=0:
            q = inletPort["fpo:hasFlowRate"]
            q2 = outletPort["fpo:hasFlowRate"]
            A = inletPort["fpo:hasCrossSectionalArea"]
            A2 = outletPort["fpo:hasCrossSectionalArea"]
            v2 = outletPort["fpo:hasVelocity"]           
            #Linnear interpolating theta
            if round(A2/A,1) <= 0.1:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [0.13, 0.20, 0.90, 2.88, 6.25, 11.88, 18.62, 26.88, 36.45]
              theta = np.interp(q2/q, xp, fp)
            
            if round(A2/A,1) > 0.1 and round(A2/A,1) <= 0.2:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [0.16, 0.13, 0.13, 0.20, 0.37, 0.90, 1.71, 2.88, 4.46]
              theta = np.interp(q2/q, xp, fp)

            if round(A2/A,1) > 0.2 and round(A2/A,1) <= 0.3:
              xp = [0.1, 0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [0.15, 0.15, 0.13, 0.14, 0.17, 0.20, 0.33, 0.50, 0.90]
              theta = np.interp(q2/q, xp, fp)

            if round(A2/A,1) > 0.3 and round(A2/A,1) <= 0.4:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [0.16, 0.16, 0.14, 0.13, 0.14, 0.13, 0.18, 0.20, 0.30]
              theta = np.interp(q2/q, xp, fp)

            if round(A2/A,1) > 0.4 and round(A2/A,1) <= 0.5:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [0.28, 0.28, 0.15, 0.14, 0.13, 0.14, 0.16, 0.15, 0.19]
              theta = np.interp(q2/q, xp, fp)

            if round(A2/A,1) > 0.5 and round(A2/A,1) <= 0.6:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [0.16, 0.16, 0.16, 0.15, 0.14, 0.13, 0.14, 0.14, 0.16]
              theta = np.interp(q2/q, xp, fp)

            if round(A2/A,1) > 0.6 and round(A2/A,1) <= 0.7:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [0.20, 0.20, 0.20, 0.15, 0.14, 0.14, 0.13, 0.13, 0.15]
              theta = np.interp(q2/q, xp, fp)
              
            if round(A2/A,1) > 0.7 and round(A2/A,1) <= 0.8:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [0.16, 0.16, 0.16, 0.16, 0.15, 0.14, 0.15, 0.13, 0.14]
              theta = np.interp(q2/q, xp, fp)
              
            if round(A2/A,1) >= 0.9:
              xp = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
              fp = [0.34, 0.34, 0.34, 0.34, 0.15, 0.15, 0.14, 0.14, 0.13]
              theta = np.interp(q2/q, xp, fp)
    
            fluidTemperature = outletPort["fpo:hasTemperature"] # *C
            fluid_vapour = Fluid(PureFluids.Air)
            fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature)) 
            density = fluid_vapour.density #kg/m3
            pressureDropValue = 0.5*density*math.pow(v2,2)*theta

            pressureDropID = "inst:"+str(uuid.uuid4())
            portData = {
            "@id" : outletPort["@id"],
            "hasPressureDrop" : pressureDropID
            }
            pressureDropData={ 
              "@id" : pressureDropID,
            "fpo:hasValue" : pressureDropValue
            }
            AfgreningArray.append(portData)
            AfgreningArray.append(pressureDropData)


      return AfgreningArray
def AfgreningWaterPressureCalculation(component):
  inletPort ={}
  outletPort ={}
  for port in component["hasPort"]:
    if port["hasFlowDirection"] == "In":
      inletPort = port
      AfgreningArray =[]

      for newPort in component["hasPort"]:
        if newPort["hasFlowDirection"] == "Out":
          outletPort = newPort
          z11 = inletPort["hasFlowDirectionVectorZ"][0]
          z12 = inletPort["hasFlowDirectionVectorZ"][1]
          z13 = inletPort["hasFlowDirectionVectorZ"][2]
          z21 = outletPort["hasFlowDirectionVectorZ"][0]
          z22 = outletPort["hasFlowDirectionVectorZ"][1]
          z23 = outletPort["hasFlowDirectionVectorZ"][2]
          z1 =z11 + z21
          z2 =z12 + z22
          z3 =z13 + z23

          if z1 ==0 and z2 ==0 and z3 ==0:
            v = inletPort["fpo:hasVelocity"]
            v1 = outletPort["fpo:hasVelocity"]
           
            #Linnear interpolating theta
            xp = [0.5, 1]
            fp = [1, 0]
            theta = np.interp(v1/v, xp, fp)
            fluidTemperature = outletPort["fpo:hasTemperature"] # *C
            fluid_vapour = Fluid(PureFluids.Water)
            fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature)) 
            density = fluid_vapour.density #kg/m3
            pressureDropValue =0.5*density*math.pow(v1,2)*theta

            pressureDropID = "inst:"+str(uuid.uuid4())
            portData = {
            "@id" : outletPort["@id"],
            "hasPressureDrop" : pressureDropID
            }
            pressureDropData={ 
              "@id" : pressureDropID,
            "fpo:hasValue" : pressureDropValue
            }
            AfgreningArray.append(portData)
            AfgreningArray.append(pressureDropData)

            
          if z1 !=0 or z2 !=0 or z3 !=0:
            v = inletPort["fpo:hasVelocity"]
            v2 = outletPort["fpo:hasVelocity"]
                        
            #Linnear interpolating theta
            xp = [0.4, 0.6, 0.8, 1, 2]
            fp = [7, 3.5, 2.5 , 2, 1]
            theta = np.interp(v2/v, xp, fp)        
            fluidTemperature = outletPort["fpo:hasTemperature"] # *C
            fluid_vapour = Fluid(PureFluids.Water)
            fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature)) 
            density = fluid_vapour.density #kg/m3
            pressureDropValue = 0.5*density*math.pow(v2,2)*theta

            pressureDropID = "inst:"+str(uuid.uuid4())
            portData = {
            "@id" : outletPort["@id"],
            "hasPressureDrop" : pressureDropID
            }
            pressureDropData={ 
              "@id" : pressureDropID,
            "fpo:hasValue" : pressureDropValue
            }
            AfgreningArray.append(portData)
            AfgreningArray.append(pressureDropData)


      return AfgreningArray

def TransitionFluids(id, temperature, fluidType, velocity, outletDiameter,inletDiameter, system, length):
    TransitionArray=[]
    fluidTemperature = temperature # *C
    if(fluidType == "Air"):
        fluid_vapour = Fluid(PureFluids.Air)
    if(fluidType == "Water"):
        fluid_vapour = Fluid(PureFluids.Water)

    fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature))

    density = fluid_vapour.density #kg/m3

    if(system=="fso:SupplySystem"):
        d1 = max(outletDiameter, inletDiameter)
        d2 = min(outletDiameter, inletDiameter)   
        K = fluids.fittings.contraction_conical_Crane(d1,d2, l=length)
    
    if(system=="fso:ReturnSystem"):
        d1 = min(outletDiameter, inletDiameter)
        d2 = max(outletDiameter, inletDiameter)   
        K = fluids.fittings.diffuser_conical(d1,d2,l=length,method="Crane") 
        
    pressureDropValue = fluids.dP_from_K(K, rho=density, V=velocity)  

    pressureDropID = "inst:"+str(uuid.uuid4())
    TransitionData = {
    "@id" : id,
    "hasPressureDrop" : pressureDropID
    }
    pressureDropData={ 
      "@id" : pressureDropID,
    "fpo:hasValue" : pressureDropValue
    }
    TransitionArray.append(TransitionData)
    TransitionArray.append(pressureDropData)
    return TransitionArray

def ElbowFluids(id, temperature, fluidType, angle, rough, velocity, diameter):
    ElbowArray = []
    fluidTemperature = temperature # *C
    if(fluidType == "Air"):
        fluid_vapour = Fluid(PureFluids.Air)
    if(fluidType == "Water"):
        fluid_vapour = Fluid(PureFluids.Water)

    fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature))

    density = fluid_vapour.density #kg/m3
    dynamic_viscosity = fluid_vapour.dynamic_viscosity #Pascal pr. second

    rougness = fluids.core.relative_roughness(D:=diameter,roughness=rough/1000) # Relative roughness
    Re = fluids.Reynolds(V=velocity, D=diameter, rho=density, mu=dynamic_viscosity) #Reynoldstal
    fd = fluids.fittings.friction_factor(Re, eD=rougness) #Frictions koefficient
    K = fluids.fittings.bend_rounded(Di=diameter, angle=angle, fd=fd, roughness=rougness)

    pressureDropValue = fluids.dP_from_K(K, rho=density, V=velocity)  

    pressureDropID = "inst:"+str(uuid.uuid4())
    ElbowData = {
    "@id" : id,
    "hasPressureDrop" : pressureDropID
    }
    pressureDropData={ 
      "@id" : pressureDropID,
    "fpo:hasValue" : pressureDropValue
    }
    ElbowArray.append(ElbowData)
    ElbowArray.append(pressureDropData)
    return ElbowArray




def pipeFluids(id, temperature, fluidType, length, rough, velocity, diameter):
    PipeArray = []

    fluidTemperature = temperature # *C
    if(fluidType == "Air"):
        fluid_vapour = Fluid(PureFluids.Air)
    if(fluidType == "Water"):
        fluid_vapour = Fluid(PureFluids.Water)

    fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature))

    density = fluid_vapour.density #kg/m3
    dynamic_viscosity = fluid_vapour.dynamic_viscosity #Pascal pr. second

    rougness = fluids.core.relative_roughness(D:=diameter,roughness=rough/1000) # Relative roughness
    Re = fluids.Reynolds(V=velocity, D=diameter, rho=density, mu=dynamic_viscosity) #Reynoldstal
    fd = fluids.fittings.friction_factor(Re, eD=rougness) #Frictions koefficient
    K = fluids.core.K_from_f(fd=fd, L=length, D=diameter)

    pressureDropValue = fluids.dP_from_K(K, rho=density, V=velocity)  

    pressureDropID = "inst:"+str(uuid.uuid4())
    PipeData = {
    "@id" : id,
    "hasPressureDrop" : pressureDropID
    }
    pressureDropData={ 
      "@id" : pressureDropID,
    "fpo:hasValue" : pressureDropValue
    }
    PipeArray.append(PipeData)
    PipeArray.append(pressureDropData)
    return PipeArray