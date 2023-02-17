import requests
import argparse
import json
import csv
import urllib.request

# add api version
basepath = "https://cloudbilling.googleapis.com/v1/"
servicespath = "services"
pricepath = "services"
requiredLocations = ['global', 'europe-west1', 'europe-west1' , 'europe-west3' , 'europe-north1']
filename_skulist = "skus_list.csv" 
filename_services = "services_skus.csv"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", help="the API key to be used with Billing API")
    args = parser.parse_args()
    if (args.key == ""):
      print ("Error please provide a key with --key option")
    URL = basepath + servicespath + "?key=" + args.key
    payload = callUrl(URL)
    data = json.loads(payload)
    writeServicesToCsv(data,args.key)

def writeServicesToCsv(data,key):
  with open(filename_services, mode='w') as servicesku_file:
    servicesku_writer = csv.writer(servicesku_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    servicesku_writer.writerow([ 'serviceId','displayName' ])
    filename = "skus_list" 
    with open(filename_skulist, mode='w') as skulist_file:
      skulist_writer = csv.writer(skulist_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      skulist_writer.writerow([ "skuId", "name", "description" , "serviceProviderName" , "region", "serviceDisplayName", "resourceFamily","resourceGroup","usageType","effectiveTime","summary","currencyConversionRate","displayQuantity","usageUnit","usageUnitDescription","aggregationLevel","aggregationInterval","aggregationCount","startUsageAmount","currencyCode","units","nanos"])        
      # for each service found we query the corresponding queue list
      for service in data['services']:
        servicesku_writer.writerow([ service['serviceId'],service['displayName'] ])
        costpayload = getSkus(service['serviceId'], key)
        unpackSku(service['serviceId'],costpayload,skulist_writer)
          
def unpackSku(serviceid,payload,skulist_writer):
    for skus in payload['skus']:
      region_string=""
      is_global_or_eu= False
      if any(location in skus['serviceRegions'] for location in requiredLocations): 
        is_global_or_eu = True
        if (skus["serviceProviderName"] .find("Google") == -1):
        # quick fix to avoid recording Skus that do not belong to Google
          is_global_or_eu= False
        if (is_global_or_eu):
        # print only global or european services
          skuid=skus["skuId"]
          name=skus["name"]
          description=skus["description"]
          serviceProviderName=skus["serviceProviderName"]
          regions=skus['serviceRegions']
          serviceDisplayName=skus["category"]["serviceDisplayName"]
          resourceFamily=skus["category"]["resourceFamily"]
          resourceGroup=skus["category"]["resourceGroup"]
          usageType=skus["category"]["usageType"]
          for pricinginfo in skus['pricingInfo']:
            effectiveTime=pricinginfo["effectiveTime"]
            summary=pricinginfo["summary"]
            currencyConversionRate=str(pricinginfo["currencyConversionRate"])
            pricingExpression = pricinginfo['pricingExpression']
            displayQuantity=str(pricingExpression["displayQuantity"])
            usageUnit=pricingExpression["usageUnit"]
            usageUnitDescription=pricingExpression["usageUnitDescription"]
            aggregationLevel=""
            aggregationInterval=""
            aggregationCount=""
            if ("aggregationInfo" in pricinginfo):
              aggregation_info = pricinginfo['aggregationInfo']
              aggregationLevel = str(aggregation_info["aggregationLevel"])
              aggregationInterval =  str(aggregation_info["aggregationInterval"])
              aggregationCount = str(aggregation_info["aggregationCount"])            
            for tieredRates in pricingExpression["tieredRates"]:
              startUsageAmount = str(tieredRates["startUsageAmount"])
              currencyCode = str(tieredRates["unitPrice"]["currencyCode"])
              units = str(tieredRates["unitPrice"]["units"])
              nanos = str(tieredRates["unitPrice"]["nanos"])
              try:
                skulist_writer.writerow([unicodify(skuid),unicodify(name),unicodify(description),unicodify(serviceProviderName),unicodify(regions),unicodify(serviceDisplayName),unicodify(resourceFamily),unicodify(resourceGroup),unicodify(usageType),unicodify(effectiveTime),unicodify(summary),unicodify(currencyConversionRate),unicodify(displayQuantity),(usageUnit),unicodify(usageUnitDescription),unicodify(aggregationLevel),unicodify(aggregationInterval),unicodify(aggregationCount),unicodify(startUsageAmount),unicodify(currencyCode),unicodify(units),unicodify(nanos)])
              except UnicodeEncodeError:
                print("Exception Unicode")
                print(skuid+ " VAR " +name+ " VAR " +description+ " VAR " +serviceProviderName+ " VAR " +regions+ " VAR " +serviceDisplayName+ " VAR " +resourceFamily+ " VAR " +resourceGroup+ " VAR " +usageType+ " VAR " +effectiveTime+ " VAR " +summary+ " VAR " +currencyConversionRate+ " VAR " +displayQuantity+ " VAR " +usageUnit+ " VAR " +usageUnitDescription+ " VAR " +aggregationLevel+ " VAR " +aggregationInterval+ " VAR " +aggregationCount+ " VAR " +currencyCode+ " VAR " +units+ " VAR " +nanos)

def getSkus(productId,apikey):
    print('Obtaining pricing info about SKU '+productId)
    URL = basepath + pricepath + "/" + productId + "/skus?key=" + apikey
    print(URL)
    payload = callUrl(URL)
    data = json.loads(payload)
    return data

def callUrl(pathtocall):
    try:
      response = urllib.request.urlopen(pathtocall)
      str_response = response.read().decode('utf-8')
      return str_response
    except urllib.error.HTTPError:
      print ("Error from sderver")
    except urllib.error.URLError:
      print ("Error reading URL")
    return ""

def unicodify(stringToUnicodify):
  return stringToUnicodify.encode('utf-8')

if __name__== "__main__":
    print ("Running Billing estimations")
    main()
