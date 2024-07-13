import { BuildingDetails } from "../building";

export interface IChatData {
  sender: {
    id: string;
    fullName: string;
    profilePictureURI?: string;
  };
  content: OneToOneChat;
  building_contents?: BuildingDetails[];
}

export interface OneToOneChat {
  id: string;
  chatContent: string;
  senderId: string;
  senderFullName: string;
  senderProfilePictureUri?: string;
  createdAt: string;
}
