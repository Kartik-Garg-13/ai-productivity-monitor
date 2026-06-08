/** Shared upload configuration for the HRMS */

export const ALLOWED_EXTENSIONS = [
  ".pdf",
  ".doc",
  ".docx",
  ".png",
  ".jpg",
  ".jpeg",
  ".xls",
  ".xlsx",
  ".zip",
];

export const ALLOWED_MIME_TYPES = [
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "image/png",
  "image/jpeg",
  "image/jpg",
  "application/vnd.ms-excel",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/zip",
  "application/x-zip-compressed",
];

export const IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"];
export const PDF_EXTENSIONS = [".pdf"];

export const DEFAULT_MAX_SIZE_MB = 10;
export const DEFAULT_MAX_SIZE_BYTES = DEFAULT_MAX_SIZE_MB * 1024 * 1024;

export const ACCEPT_STRING = ALLOWED_EXTENSIONS.join(",");

export const IMAGE_ACCEPT = ".png,.jpg,.jpeg,image/png,image/jpeg";

export function formatFileSize(bytes) {
  if (!bytes && bytes !== 0) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export function getFileExtension(name = "") {
  const idx = name.lastIndexOf(".");
  return idx >= 0 ? name.slice(idx).toLowerCase() : "";
}

export function isImageFile(file) {
  if (!file) return false;
  const ext = getFileExtension(file.name);
  return IMAGE_EXTENSIONS.includes(ext) || (file.type || "").startsWith("image/");
}

export function isPdfFile(file) {
  if (!file) return false;
  return getFileExtension(file.name) === ".pdf" || file.type === "application/pdf";
}
