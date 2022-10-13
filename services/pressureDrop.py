from textwrap import indent
import fluids
from rdflib import Graph, RDF, Namespace
from pyfluids import Fluid, PureFluids, Input
import json
import math

def test(graph): 
  ###Extracting data at component level and send it to fluid component
  distributionComponents ={
  "@graph" : [ ],
  "@context" : {
    "hasSystem" : {
      "@id" : "http://w3id.org/fso#hasSystem",
      "@type" : "@id"
    },
    "outerDiameter" : {
      "@id" : "http://w3id.org/fpo#outerDiameter",
      "@type" : "http://www.w3.org/2001/XMLSchema#double"
    },
    "length" : {
      "@id" : "http://w3id.org/fpo#length",
      "@type" : "http://www.w3.org/2001/XMLSchema#double"
    },
    "flowRate" : {
      "@id" : "http://w3id.org/fpo#flowRate",
      "@type" : "http://www.w3.org/2001/XMLSchema#double"
    },
    "roughness" : {
      "@id" : "http://w3id.org/fpo#roughness",
      "@type" : "http://www.w3.org/2001/XMLSchema#double"
    },
    "velocity" : {
      "@id" : "http://w3id.org/fpo#velocity",
      "@type" : "http://www.w3.org/2001/XMLSchema#double"
    },
    "temperature" : {
      "@id" : "http://w3id.org/fpo#temperature",
      "@type" : "http://www.w3.org/2001/XMLSchema#double"
    },
    "flowType" : {
      "@id" : "http://w3id.org/fpo#flowType"
    },
    "angle" : {
      "@id" : "http://w3id.org/fpo#angle",
      "@type" : "http://www.w3.org/2001/XMLSchema#double"
    },
    "ex" : "https://example.com/ex#",
    "fso" : "http://w3id.org/fso#",
    "bot" : "https://w3id.org/bot#",
    "xsd" : "http://www.w3.org/2001/XMLSchema#",
    "rdfs" : "http://www.w3.org/2000/01/rdf-schema#",
    "sh" : "http://www.w3.org/ns/shacl#",
    "fpo" : "http://w3id.org/fpo#",
    "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "inst" : "https://example.com/inst#"
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
              flowDirection = item2["flowDirection"]
              flowType = item2["flowType"]
              temperature = item2["fpo:temperature"]
              velocity = item2["fpo:velocity"]

              
              portArray.append({
                "@id": item2["@id"],
                "flowDirection": flowDirection,
                "flowType": flowType,
                "fpo:temperature": temperature,
                "fpo:velocity": velocity,
                "hasFlowDirectionVectorZ": directionVectorArray
              })

              #if "fpo:velocity" not in i:
                #print(port, revitID)
                #counter +=1
      Tee ={"@id": item1["@id"], "hasPort":portArray}
      TeeComponents["@graph"].append(Tee)
      #print(portArray)
  # Identify TEE and calculate
  print((TeeIdentifier(TeeComponents)))
  # for item1 in TeeComponents["@graph"]:
  #   for item2 in item1["hasPort"]:
  #     print(item2["ex:hasFlowDirectionVectorZ"])
  # #Calculate pressure drop for each pipe and duct and add it to object
  # if (i['@type'] =='fso:Pipe' or i['@type'] =='fso:Duct'):
  #     result=pipeFluids(i["@id"], i["fpo:temperature"], i["flowType"], i["fpo:length"], i["fpo:roughness"], i["fpo:velocity"], i["fpo:outerDiameter"])

  #     distributionComponents["@graph"].append(result)
  
  # #Calculate pressure drop for each elbow and add it to object
  # if (i['@type'] =='fso:Elbow'):
  #     result=ElbowFluids(i["@id"], i["fpo:temperature"], i["flowType"], i["fpo:angle"], i["fpo:roughness"], i["fpo:velocity"], i["fpo:outerDiameter"])

  #     distributionComponents["@graph"].append(result)

  # #Calculate pressure drop for each transition and add it to object
  # if (i['@type'] =='fso:Transition'):
  #     result=TransitionFluids(i["@id"], i["fpo:temperature"], i["flowType"], i["fpo:velocity"], i["fpo:outerDiameter"],i["fpo:innerDiameter"], i["hasSystem"], i["fpo:length"])

  #     distributionComponents["@graph"].append(result)

  
          
  return TeeComponents#TeeComponents #distributionComponents #json.dumps(distributionComponents)


###Based on the flow direction vector we identify each Tee type and send it to the pressure calculator. We also return the result of the pressure drop and adds it to component. 
def TeeIdentifier (Tees):
  for component in Tees["@graph"]: 
    inletArray =[]
    outletArray=[]
    for port in component["hasPort"]:
      directionVectorArray = []
      if port["flowDirection"] == "In":
        inletArray.append(port["hasFlowDirectionVectorZ"])
      if port["flowDirection"] == "Out":
        outletArray.append(port["hasFlowDirectionVectorZ"])
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
        if port["flowType"] =="Water":
          print("Sammenlob Water")
        else:
          print("Sammenlob Air")
          
      else:
        if port["flowType"] =="Water":
          print("Tillob Water")
        if port["flowType"] =="Air":
          print("Tillob Air")


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
        if port["flowType"] =="Water":
          print("Fordeling Water")
        else:
          print("Fordeling Air")
      else:
        if port["flowType"] =="Water":
          AfgreningWaterPressureCalculation(component)
          print("Afgrening Water")
        if port["flowType"] =="Air":
          print("Afgrening Air") 

  return "count"


def AfgreningWaterPressureCalculation(component):
  inletPort ={}
  outletPort ={}
  for port in component["hasPort"]:
    if port["flowDirection"] == "In":
      inletPort = port
      for newPort in component["hasPort"]:
        if newPort["flowDirection"] == "Out":
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
            v = inletPort["fpo:velocity"]
            v1 = outletPort["fpo:velocity"]
            
            #Linnear interpolating theta
            theta = (((v1/v)-0.5)/(1-0.5))*(0-0.5)+0.5
            fluidTemperature = outletPort["fpo:temperature"] # *C
            fluid_vapour = Fluid(PureFluids.Water)
            fluid_vapour.update(Input.Pressure.with_value(101325), Input.Temperature.with_value(273.15+fluidTemperature)) 
            density = fluid_vapour.density #kg/m3
            pressureDrop =0.5*density*math.pow(v1,2)*theta
            print(pressureDrop)




def TransitionFluids(id, temperature, fluidType, velocity, outletDiameter,inletDiameter, system, length):
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
        
    pressure = fluids.dP_from_K(K, rho=density, V=velocity)  

    pipeFittingObject = {
    "@id" : id,
    "fpo:value" : pressure
    }
    print(id, pressure) 

    return pipeFittingObject

def ElbowFluids(id, temperature, fluidType, angle, rough, velocity, diameter):
    print(diameter)

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

    pressure = fluids.dP_from_K(K, rho=density, V=velocity)  

    pipeFittingObject = {
    "@id" : id,
    "fpo:value" : pressure
    }
    print(id, pressure) 

    return pipeFittingObject




def pipeFluids(id, temperature, fluidType, length, rough, velocity, diameter):
    print(diameter)

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

    pressure = fluids.dP_from_K(K, rho=density, V=velocity)  

    pipeFittingObject = {
    "@id" : id,
    "fpo:value" : pressure
    }
    print(id, pressure/length) 

    return pipeFittingObject