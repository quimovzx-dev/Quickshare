const fileInput = document.getElementById("fileInput");
const fileList = document.getElementById("fileList");
const uploadStatus = document.getElementById("uploadStatus");
const refreshBtn = document.getElementById("refreshBtn");

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  return `${(bytes / 1024 / 1024 / 1024).toFixed(1)} GB`;
}

async function loadFiles() {
  fileList.innerHTML = '<p class="muted">Loading files...</p>';
  try {
    const response = await fetch("/api/files");
    const files = await response.json();

    if (!files.length) {
      fileList.innerHTML = '<p class="muted">No files uploaded yet.</p>';
      return;
    }

    fileList.innerHTML = files.map(file => `
      <div class="file-item">
        <div>
          <div class="file-name">${escapeHtml(file.name)}</div>
          <div class="file-meta">${formatBytes(file.size)} · ${new Date(file.modified).toLocaleString()}</div>
        </div>
        <div class="actions">
          <a class="action" href="/api/download/${encodeURIComponent(file.name)}">Download</a>
          <button class="action delete" onclick="deleteFile('${encodeURIComponent(file.name)}')">Delete</button>
        </div>
      </div>
    `).join("");
  } catch (error) {
    fileList.innerHTML = '<p class="muted">Could not load files.</p>';
  }
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[char]));
}

fileInput.addEventListener("change", async () => {
  const files = [...fileInput.files];
  if (!files.length) return;

  uploadStatus.textContent = `Uploading ${files.length} file(s)...`;

  for (const file of files) {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/upload", { method: "POST", body: formData });
      if (!response.ok) throw new Error("Upload failed");
    } catch (error) {
      uploadStatus.textContent = `Failed to upload: ${file.name}`;
      return;
    }
  }

  uploadStatus.textContent = "Upload complete!";
  fileInput.value = "";
  await loadFiles();
});

async function deleteFile(encodedName) {
  if (!confirm("Delete this file?")) return;
  await fetch(`/api/files/${encodedName}`, { method: "DELETE" });
  await loadFiles();
}

refreshBtn.addEventListener("click", loadFiles);
loadFiles();
