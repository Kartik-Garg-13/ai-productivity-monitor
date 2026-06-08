import {
  ALLOWED_EXTENSIONS,
  ALLOWED_MIME_TYPES,
  DEFAULT_MAX_SIZE_BYTES,
  getFileExtension,
} from "../constants/uploadConfig";

export function validateFile(file, options = {}) {
  const {
    maxSizeBytes = DEFAULT_MAX_SIZE_BYTES,
    allowedExtensions = ALLOWED_EXTENSIONS,
    allowedMimeTypes = ALLOWED_MIME_TYPES,
    existingFiles = [],
  } = options;

  if (!file) {
    return { valid: false, error: "No file selected." };
  }

  const ext = getFileExtension(file.name);
  if (!allowedExtensions.includes(ext)) {
    return {
      valid: false,
      error: `Unsupported file type "${ext || "unknown"}". Allowed: ${allowedExtensions.join(", ")}`,
    };
  }

  if (file.type && !allowedMimeTypes.includes(file.type) && !file.type.startsWith("image/")) {
    const extOk = allowedExtensions.includes(ext);
    if (!extOk) {
      return { valid: false, error: `Invalid file format: ${file.type}` };
    }
  }

  if (file.size > maxSizeBytes) {
    const maxMb = (maxSizeBytes / (1024 * 1024)).toFixed(0);
    return { valid: false, error: `File exceeds ${maxMb} MB size limit.` };
  }

  if (file.size === 0) {
    return { valid: false, error: "File is empty." };
  }

  const duplicate = existingFiles.some(
    (f) => f && f.name === file.name && f.size === file.size && f.lastModified === file.lastModified
  );
  if (duplicate) {
    return { valid: false, error: `"${file.name}" is already selected.` };
  }

  return { valid: true, error: null };
}

export function validateFiles(files, options = {}) {
  const { multiple = false, maxFiles = 10, ...rest } = options;
  if (!files?.length) {
    return { valid: false, error: "No file selected.", files: [] };
  }
  if (!multiple && files.length > 1) {
    return { valid: false, error: "Only one file allowed.", files: [] };
  }
  if (files.length > maxFiles) {
    return { valid: false, error: `Maximum ${maxFiles} files allowed.`, files: [] };
  }

  const accepted = [];
  for (const file of files) {
    const result = validateFile(file, { ...rest, existingFiles: accepted });
    if (!result.valid) return { valid: false, error: result.error, files: accepted };
    accepted.push(file);
  }
  return { valid: true, error: null, files: accepted };
}
