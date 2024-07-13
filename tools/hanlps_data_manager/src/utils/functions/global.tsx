import { URLSearchParams } from "url";

// Whatsapp sender
export function sendWACS() {
  // Send static Whatsapp messages to Customer Service
  // TODO: Insert the Whatsapp number to ENV
  return window.open(
    `https://wa.me/${6281280111698}?text=Hi%20kak%20mau%20nanya%20dong%20!%20!%20!`,
    "_blank"
  );
}

export function smoothScrollTop() {
  window.scrollTo({
    top: 0,
    left: 0,
    behavior: "smooth",
  });
}

export const delayInMilliSecond = (ms: number) =>
  new Promise((res) => setTimeout(res, ms));

export const clearAllUrlParameters = () => {
  const currentUrl = new URL(window.location.href);
  currentUrl.search = "";
  window.history.replaceState({}, "", currentUrl.href);
};

export const getURLParams = (
  url: URLSearchParams,
  key: string
) => url.get(key);

export const setURLParams = (
  url: URLSearchParams,
  key: string,
  val: string
) => {
  url.set(key, val);
  const newUrl = url.toString();
  window.history.pushState({}, "", newUrl);
};

export const removeTrailingNewlines = (str: string) => {
  if (!str) return "";
  return str.replace(/\n+$/, "");
};

export const removeLeadingZeros = (str: string) => {
  // Use regular expression to remove leading zeros
  return str.replace(/^0+/, "");
};

export const formattedNumber = (number: number) => {
  if (isNaN(number)) number = 0;
  return new Intl.NumberFormat().format(number);
};

export const unformattedNumber = (
  formattedString: string
) => {
  // Remove any non-numeric characters and parse the string to a number
  const unformattedString = formattedString.replace(
    /[^\d.-]/g,
    ""
  );
  return parseFloat(unformattedString);
};

export const acceptNumericOnly = (input: string) => {
  // Remove any non-numeric characters
  input = input.replace(/[^0-9]/g, "");
  return input;
};

export const formatDateID = (date: string) => {
  const inputDate = new Date(date);

  // Indonesian days of the week
  const indonesianDaysOfWeek = [
    "Minggu",
    "Senin",
    "Selasa",
    "Rabu",
    "Kamis",
    "Jumat",
    "Sabtu",
  ];

  const dayName =
    indonesianDaysOfWeek[inputDate.getUTCDay()];
  const day = inputDate.getUTCDate();
  const month = inputDate.getUTCMonth() + 1;
  const year = inputDate.getUTCFullYear();

  const formattedDate = `${dayName}, ${day
    .toString()
    .padStart(2, "0")}-${month
    .toString()
    .padStart(2, "0")}-${year}`;

  return formattedDate;
};
