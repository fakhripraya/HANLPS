export interface MasterModel {
  data: BuildingModel[];
}

export interface BuildingModel {
  index?: number;
  building_title?: string;
  building_address?: string;
  building_facility?: string;
  building_landmarks?: string;
  building_description?: string;
  housing_price?: string;
  owner_name?: string;
  owner_whatsapp?: string;
  owner_phone_number?: string;
  owner_email?: string;
  image_urls?: string[];
  isReady?: boolean;
}
