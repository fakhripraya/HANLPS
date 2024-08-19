export interface BuildingModel {
  building_title?: string;
  building_address?: string;
  building_proximity_string?: string;
  building_proximity?: string[];
  building_facility_string?: string;
  building_facility?: string[];
  building_description?: string;
  housing_price?: string;
  owner_name?: string;
  owner_whatsapp?: string;
  owner_phone_number?: string;
  owner_email?: string;
  image_urls?: string[];
  isReady?: boolean;
}

export interface EditedBuildingModel extends BuildingModel {
  index?: number;
  isEdited?: boolean;
}

export interface MasterData {
  data: BuildingModel[];
}
