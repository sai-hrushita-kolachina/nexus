export function formatDate(dateString) {
  if (!dateString) {
    return "";
  }

  const date = new Date(dateString);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  const now = new Date();

  const difference =
    now.getTime() - date.getTime();

  const minutes =
    Math.floor(difference / 60000);

  if (minutes < 1) {
    return "Just now";
  }

  if (minutes < 60) {
    return `${minutes}m ago`;
  }

  const hours =
    Math.floor(minutes / 60);

  if (hours < 24) {
    return `${hours}h ago`;
  }

  const days =
    Math.floor(hours / 24);

  if (days < 7) {
    return `${days}d ago`;
  }

  return date.toLocaleDateString();
}

export function formatFileSize(bytes) {
  if (!bytes) {
    return "Unknown size";
  }

  const units = [
    "B",
    "KB",
    "MB",
    "GB",
  ];

  let size = bytes;
  let unitIndex = 0;

  while (
    size >= 1024 &&
    unitIndex < units.length - 1
  ) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
}

export function getFileIcon(filename) {
  const extension =
    filename
      ?.split(".")
      .pop()
      ?.toLowerCase();

  if (extension === "pdf") {
    return "PDF";
  }

  if (extension === "docx") {
    return "DOC";
  }

  if (extension === "txt") {
    return "TXT";
  }

  return "FILE";
}

export function truncateText(
  text,
  length = 60
) {
  if (!text) {
    return "";
  }

  if (text.length <= length) {
    return text;
  }

  return `${text.slice(0, length)}...`;
}