export interface MasterModel {
  data: Data;
  paginationToken: string;
}

export interface Data {
  items: ItemModel[];
}

export interface ItemModel {
  carousel_media: CarouselData[];
  caption: CaptionData;
}

export interface CarouselData {
  thumbnail_url: string;
}

export interface CaptionData {
  text: string;
}

export interface BuildingModel {
  building_title?: string;
  building_address?: string;
  building_description?: string;
  housing_price?: string;
  owner_name?: string;
  owner_whatsapp?: string;
  owner_phone_number?: string;
  owner_email?: string;
  image_urls?: string[];
}
