#!/usr/bin/python
#
#	Add BEP Demolition check and update query appropriately.
#
#
import psycopg2
import sys
# import argparse
#
# parser = argparse.ArgumentParser(description='Generate SQL to add property to Blight Fight')
# parser.add_argument('-p', '--parcel', type=int, help='parcel number', required=False)
#
# parser.add_argument('--nsp', dest='feature', action='store_true')
# parser.add_argument('--no-nsp', dest='feature', action='store_false')
#
# parser.add_argument('--nsp', dest='feature', action='store_true')
# parser.add_argument('--no-nsp', dest='feature', action='store_false')
#
# parser.add_argument('--nsp', dest='feature', action='store_true')
# parser.add_argument('--no-nsp', dest='feature', action='store_false')


conn_string_gis = "host='localhost' dbname='gis' user='chris' password='chris'"
conn_gis = psycopg2.connect(conn_string_gis)
cursor_gis = conn_gis.cursor()

conn_string_geodjango = "host='localhost' dbname='blight_fight' user='chris' password='chris'"
conn_geodjango = psycopg2.connect(conn_string_geodjango)
cursor_geodjango = conn_geodjango.cursor()


def getStreetAddress(parcel, cursor):
	cursor.execute('SELECT "streetAddress" FROM parcels where parcel_c =\''+str(parcel)+'\'')
	try:
		return cursor.fetchone()[0]
	except:
		raise ValueError('No street address found')
		return False

def getWithin(parcel, within, cursor_gis, cursor_geodjango):
	cursor_gis.execute("SELECT ST_AsText(ST_Transform(st_centroid(geom), 4326)) FROM parcels WHERE parcel_c = '"+str(parcel)+"'")
	geom = cursor_gis.fetchone()
	if not geom:
		return False

	#cursor_geodjango.execute('SELECT id FROM '+str(within)+' w WHERE ST_Contains(w.geometry, ST_SetSRID(ST_GeomFromText(\''+str(geom[0])+'\'), 4326)) OR ST_Overlaps(w.geometry, ST_SetSRID(ST_GeomFromText(\''+str(geom[0])+'\'), 4326))')
	cursor_geodjango.execute('SELECT id FROM '+str(within)+' w WHERE ST_WITHIN(ST_SetSRID(ST_GeomFromText(\''+str(geom[0])+'\'), 4326), st_transform(w.geometry, 4326))')
	#print 'SELECT id FROM '+str(within)+' w WHERE ST_WITHIN(ST_SetSRID(ST_GeomFromText(\''+str(geom[0])+'\'), 4326), st_transform(w.geometry, 4326))'

	try:
		return cursor_geodjango.fetchone()[0]
	except:
		#raise ValueError('No '+within+' found')
		return 'NULL'

def getStructureType(parcel, cursor):
	cursor.execute("SELECT improv_value FROM counter_book_2017 WHERE parcel_number = '"+str(parcel)+"'")
	try:
		grossimprovedvalue = int(cursor.fetchone()[0])
		if (grossimprovedvalue > 0):
			return "Residential Dwelling"
		else:
			return "Vacant Lot"
	except:
		return False

def getSidelotEligible(parcel, cursor, structureType):
	#if getStructureType(parcel, cursor) != 'Vacant Lot': return False
	cursor.execute("select count(b2.*) from parcels p2 left join (select p.\"streetAddress\", p.parcel_c, p.geom from parcels p where p.parcel_c in(select parcel from improvement_location_permits where permit_type = 'PRIMARY' and status = 'Issued' group by parcel) ) as b on st_dwithin(p2.geom, b.geom, 1320) left join improvement_location_permits b2 on b2.parcel=b.parcel_c where p2.parcel_c = '%s'", [parcel])
	result = cursor.fetchone()
	#print '!!!! {0}'.format(int(result[0]),)
	if int(result[0]) > 1:
		cursor.execute("select b.\"streetAddress\", b.parcel_c, b2.permit, permit_type, b2.status from parcels p2 left join (select p.\"streetAddress\", p.parcel_c, p.geom from parcels p where p.parcel_c in(select parcel from improvement_location_permits where permit_type = 'PRIMARY' and status = 'Issued' group by parcel) ) as b on st_dwithin(p2.geom, b.geom, 1320) left join improvement_location_permits b2 on b2.parcel=b.parcel_c where p2.parcel_c = '%s'", [parcel])
		result = cursor.fetchall()
		print "Conflicting ILP for sidelot eligiblity: {0}".format(result,)
		return False
	if structureType != 'Vacant Lot': # Only vacant lots can be eligible.
		return False
	return True

def getParcelArea(parcel, cursor):
	cursor.execute("SELECT round(ST_area(geom)) FROM parcels WHERE parcel_c = '"+str(parcel)+"'")
	return cursor_gis.fetchone()[0]

def getUrbanGardenStatus(parcel, cursor):
	cursor.execute("SELECT count(*) FROM urban_gardens WHERE parcel_c = '"+str(parcel)+"'")
	return cursor_gis.fetchone()[0] > 0

def getBEPDemolitionStatus(parcel, cursor):
	cursor.execute("SELECT count(*) FROM bep_demolitions WHERE parcel_c = '"+str(parcel)+"'")
	return cursor_gis.fetchone()[0] > 0

def getGeometry(parcel, cursor):
	cursor.execute("SELECT ST_Transform(geom, 4326) FROM parcels WHERE parcel_c = '"+str(parcel)+"'")
	return cursor_gis.fetchone()[0]

def getCentroidGeometry(parcel, cursor):
	cursor.execute("SELECT st_centroid(ST_Transform(geom, 4326)) FROM parcels WHERE parcel_c = '"+str(parcel)+"'")
	return cursor_gis.fetchone()[0]

def getVacantLotEligible(parcel, cursor):
	cursor.execute("SELECT c.disposition_strategy FROM property_inventory_contextarea c LEFT JOIN property_inventory_property p on st_within(p.geometry, c.geometry) WHERE p.parcel = '%s'", [parcel])
	try:
		result = cursor.fetchone()[0]
	except TypeError:
		return False
	return result == 'Sidelot / Auction Area'


parcel = input("Enter parcel number: ")
streetAddress = getStreetAddress(parcel, cursor_gis)
streetAddressInput = raw_input("Street Address [%s]: " % streetAddress)
streetAddress = streetAddressInput or streetAddress

structureType = getStructureType(parcel, cursor_gis)
structureTypeInput = raw_input("Structure Type [%s]: " % structureType)
structureType = structureTypeInput or structureType

nspInput = raw_input("NSP (y/n): ")
nsp = (nspInput in ['y','Y'])

quietTitleInput = raw_input("Quiet Title Complete (y/n): ")
quiet_title_complete = (quietTitleInput in ['y','Y'])

homesteadInput = raw_input("Homestead Only (y/N): ")
homestead_only = False or (homesteadInput in ['y', 'Y'])

price_oboInput = raw_input("Price OBO (y/N): ")
price_obo = False or (price_oboInput in ['y', 'Y'])

renew_ownedInput = raw_input("Renew Owned (y/N): ")
renew_owned = False or (renew_ownedInput in ['y', 'Y'])

hhf_demolitionInput = raw_input("HHF Demolition (y/N): ")
hhf_demolition = False or (hhf_demolitionInput in ['y', 'Y'])

is_activeInput = raw_input("Mark Active in inventory (Y/n): ")
is_active = False or (is_activeInput in ['y', 'Y'])


price_Input = raw_input("Price [$3,500]: ")
try:
	price = int(price_Input)
except ValueError:
	price = 3500

project_agreement_released = False

# if nsp:
# 	if quiet_title_complete: price = 3000
# 	else: price = 1500
# else:
# 	if quiet_title_complete: price = 3500
# 	else: price = 2000

streetAddress = getStreetAddress(parcel, cursor_gis)
zipcode_id = getWithin(parcel, "property_inventory_zipcode", cursor_gis, cursor_geodjango)
cdc_id = getWithin(parcel, "property_inventory_cdc", cursor_gis, cursor_geodjango)
zone_id = getWithin(parcel, "property_inventory_zoning", cursor_gis, cursor_geodjango)
neighborhood_id = getWithin(parcel, "property_inventory_neighborhood", cursor_gis, cursor_geodjango)
sidelot_eligible = getSidelotEligible(parcel, cursor_gis, structureType)
vacant_lot_eligible = getVacantLotEligible(parcel, cursor_geodjango)
area = getParcelArea(parcel, cursor_gis)
urban_garden_status = getUrbanGardenStatus(parcel, cursor_gis)
bep_demolition_status = getBEPDemolitionStatus(parcel, cursor_gis)
geometry = getGeometry(parcel, cursor_gis)
centroid_geometry = getCentroidGeometry(parcel, cursor_gis)

query = "INSERT INTO property_inventory_property (\"propertyType\", parcel, \"streetAddress\", nsp, quiet_title_complete, \"structureType\", cdc_id, zone_id, zipcode_id, neighborhood_id, urban_garden, bep_demolition, status, sidelot_eligible, vacant_lot_eligible, price, area, homestead_only, applicant, price_obo, project_agreement_released, is_active, renew_owned, hhf_demolition, geometry, centroid_geometry ) VALUES ('lb', '%(parcel)s', '%(streetAddress)s', %(nsp)s, %(quiet_title_complete)s, '%(structureType)s', %(cdc_id)s, %(zone_id)s, %(zipcode_id)s, %(neighborhood_id)s, %(urban_garden_status)s, %(bep_demolition_status)s,'Available', %(sidelot_eligible)s, %(vacant_lot_eligible)s, %(price)s, %(area)s, %(homestead_only)s, NULL, %(price_obo)s, %(project_agreement_released)s, %(is_active)s, %(renew_owned)s, %(hhf_demolition)s, '%(geometry)s', '%(centroid_geometry)s' )" % {"parcel": parcel, "streetAddress": streetAddress, "nsp": nsp, "quiet_title_complete": quiet_title_complete, "structureType": structureType, "cdc_id": cdc_id, "zone_id": zone_id, "zipcode_id": zipcode_id, "neighborhood_id": neighborhood_id, "sidelot_eligible": sidelot_eligible, "vacant_lot_eligible": vacant_lot_eligible, "price": price, "area": area, "homestead_only": homestead_only, "urban_garden_status": urban_garden_status, "bep_demolition_status": bep_demolition_status, "price_obo": price_obo, "project_agreement_released": project_agreement_released, "is_active": is_active, "renew_owned": renew_owned, "hhf_demolition":hhf_demolition, "geometry": geometry, "centroid_geometry": centroid_geometry}
#print query+";"
sys.stderr.write(query+";\n")
