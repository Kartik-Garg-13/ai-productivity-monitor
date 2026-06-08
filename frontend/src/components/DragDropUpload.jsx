import { useCallback, useEffect, useRef, useState } from "react";
import {
  ACCEPT_STRING,
  DEFAULT_MAX_SIZE_BYTES,
  formatFileSize,
  isImageFile,
  isPdfFile,
} from "../constants/uploadConfig";
import { validateFile, validateFiles } from "../utils/uploadValidation";

function UploadIcon() {
  return (
    <svg className="w-10 h-10 text-slate-400 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 010-9m10.5 9a4.5 4.5 0 000-9m0 9H18.75M3.75 15h16.5" />
    </svg>
  );
}

function FilePreview({ file, previewUrl, onPreviewPdf }) {
  if (!file) return null;
  if (isImageFile(file) && previewUrl) {
    return <img src={previewUrl} alt={file.name} className="h-16 w-16 object-cover rounded-lg border" />;
  }
  if (isPdfFile(file)) {
    return (
      <button
        type="button"
        onClick={onPreviewPdf}
        className="text-xs text-indigo-600 hover:underline font-medium"
      >
        Preview PDF
      </button>
    );
  }
  return (
    <div className="h-12 w-12 rounded-lg bg-slate-100 flex items-center justify-center text-slate-500 text-xs font-bold uppercase">
      {file.name.split(".").pop()?.slice(0, 4)}
    </div>
  );
}

/**
 * Reusable drag-and-drop file upload component.
 *
 * @param {File|File[]|null} value - Selected file(s)
 * @param {function} onChange - (file | File[] | null) => void
 * @param {boolean} multiple - Allow multiple files
 * @param {number} maxFiles - Max files when multiple
 * @param {string} accept - HTML accept attribute override
 * @param {number} maxSizeBytes - Max file size
 * @param {string} label - Field label
 * @param {string} hint - Helper text
 * @param {boolean} compact - Smaller drop zone
 * @param {boolean} required - Show required indicator
 * @param {function} onUpload - Optional async (file, setProgress) for immediate upload
 * @param {string} existingUrl - URL for already-uploaded file preview
 * @param {string} existingName - Name of existing file
 * @param {boolean} disabled
 */
export default function DragDropUpload({
  value = null,
  onChange,
  multiple = false,
  maxFiles = 10,
  accept = ACCEPT_STRING,
  maxSizeBytes = DEFAULT_MAX_SIZE_BYTES,
  label,
  hint,
  compact = false,
  required = false,
  onUpload,
  existingUrl,
  existingName,
  disabled = false,
  className = "",
}) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [previewUrls, setPreviewUrls] = useState({});

  const files = multiple
    ? Array.isArray(value) ? value : value ? [value] : []
    : value ? [value].flat().slice(0, 1) : [];

  useEffect(() => {
    const urls = {};
    files.forEach((f) => {
      if (f && isImageFile(f)) urls[f.name + f.lastModified] = URL.createObjectURL(f);
    });
    setPreviewUrls(urls);
    return () => Object.values(urls).forEach((u) => URL.revokeObjectURL(u));
  }, [files]);

  const applyFiles = useCallback(
    async (incoming) => {
      setError("");
      const list = multiple ? incoming : incoming.slice(0, 1);
      const result = validateFiles(list, { multiple, maxFiles, maxSizeBytes, existingFiles: multiple ? files : [] });
      if (!result.valid) {
        setError(result.error);
        return;
      }
      const selected = multiple ? result.files : result.files[0] || null;
      onChange?.(selected);

      if (onUpload && selected) {
        setUploading(true);
        setProgress(0);
        try {
          const toUpload = multiple ? selected : [selected];
          for (const f of toUpload) {
            await onUpload(f, setProgress);
          }
          setProgress(100);
        } catch (e) {
          setError(e?.response?.data?.detail || e.message || "Upload failed");
          onChange?.(multiple ? [] : null);
        } finally {
          setUploading(false);
        }
      }
    },
    [multiple, maxFiles, maxSizeBytes, files, onChange, onUpload]
  );

  const handleInput = (e) => {
    const picked = Array.from(e.target.files || []);
    if (picked.length) applyFiles(picked);
    e.target.value = "";
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
    if (disabled || uploading) return;
    const dropped = Array.from(e.dataTransfer.files || []);
    if (dropped.length) applyFiles(dropped);
  };

  const removeFile = (index) => {
    if (multiple) {
      const next = files.filter((_, i) => i !== index);
      onChange?.(next.length ? next : []);
    } else {
      onChange?.(null);
    }
    setError("");
    setProgress(0);
  };

  const openPreview = (file) => {
    const key = file.name + file.lastModified;
    const url = previewUrls[key] || URL.createObjectURL(file);
    if (isPdfFile(file)) window.open(url, "_blank", "noopener,noreferrer");
  };

  const zoneHeight = compact ? "min-h-[120px]" : "min-h-[180px]";

  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-slate-700">
          {label}
          {required && <span className="text-red-500 ml-0.5">*</span>}
        </label>
      )}

      <div
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && !disabled && inputRef.current?.click()}
        onDragEnter={(e) => { e.preventDefault(); if (!disabled) setDragging(true); }}
        onDragOver={(e) => { e.preventDefault(); if (!disabled) setDragging(true); }}
        onDragLeave={(e) => { e.preventDefault(); setDragging(false); }}
        onDrop={handleDrop}
        onClick={() => !disabled && !uploading && inputRef.current?.click()}
        className={`
          relative ${zoneHeight} w-full rounded-xl border-2 border-dashed transition-all cursor-pointer
          flex flex-col items-center justify-center p-4 text-center
          ${dragging ? "border-indigo-500 bg-indigo-50 scale-[1.01]" : "border-slate-300 bg-slate-50 hover:border-indigo-400 hover:bg-indigo-50/50"}
          ${disabled || uploading ? "opacity-60 cursor-not-allowed pointer-events-none" : ""}
        `}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept={accept}
          multiple={multiple}
          disabled={disabled || uploading}
          onChange={handleInput}
        />
        {!files.length && !existingUrl && (
          <>
            <UploadIcon />
            <p className="mt-2 text-sm font-medium text-slate-700">Drag & Drop Files Here</p>
            <p className="text-xs text-slate-500 mt-1">or click to browse</p>
            {hint && <p className="text-xs text-slate-400 mt-2">{hint}</p>}
          </>
        )}
        {(files.length > 0 || existingUrl) && !uploading && (
          <p className="text-xs text-slate-500">Drop to replace or click to browse</p>
        )}
        {uploading && (
          <div className="w-full max-w-xs">
            <p className="text-sm text-indigo-600 font-medium mb-2">Uploading…</p>
            <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-600 transition-all duration-300" style={{ width: `${progress}%` }} />
            </div>
            <p className="text-xs text-slate-500 mt-1">{progress}%</p>
          </div>
        )}
      </div>

      {existingUrl && !files.length && (
        <div className="flex items-center gap-3 p-3 bg-white border rounded-lg">
          {existingUrl.match(/\.(png|jpe?g|gif|webp)/i) ? (
            <img src={existingUrl} alt="" className="h-12 w-12 object-contain rounded" />
          ) : (
            <div className="h-12 w-12 bg-slate-100 rounded flex items-center justify-center text-xs text-slate-500">FILE</div>
          )}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{existingName || "Uploaded file"}</p>
            <a href={existingUrl} target="_blank" rel="noreferrer" className="text-xs text-indigo-600 hover:underline" onClick={(e) => e.stopPropagation()}>
              View / Download
            </a>
          </div>
        </div>
      )}

      {files.map((file, index) => (
        <div key={`${file.name}-${file.lastModified}-${index}`} className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg shadow-sm">
          <FilePreview
            file={file}
            previewUrl={previewUrls[file.name + file.lastModified]}
            onPreviewPdf={() => openPreview(file)}
          />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-800 truncate">{file.name}</p>
            <p className="text-xs text-slate-500">{formatFileSize(file.size)}</p>
            {isPdfFile(file) && (
              <button type="button" className="text-xs text-indigo-600 hover:underline mt-0.5" onClick={() => openPreview(file)}>
                Preview
              </button>
            )}
          </div>
          {!uploading && (
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); removeFile(index); }}
              className="text-red-500 hover:text-red-700 text-sm font-medium px-2 py-1 rounded hover:bg-red-50"
            >
              Remove
            </button>
          )}
        </div>
      ))}

      {error && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">{error}</p>
      )}

      {!hint && !label && (
        <p className="text-xs text-slate-400">PDF, DOC, DOCX, PNG, JPG, XLS, XLSX, ZIP — max {(maxSizeBytes / (1024 * 1024)).toFixed(0)} MB</p>
      )}
    </div>
  );
}

export { validateFile, validateFiles };
