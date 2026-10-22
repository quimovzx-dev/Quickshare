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
    if (!response.ok) throw new Error("Sign in to view files");
    const files = await response.json();

    if (!files.length) {
      fileList.innerHTML = '<p class="muted">No files uploaded yet.</p>';
      return;
    }

    fileList.replaceChildren();
    for (const file of files) {
      const row = document.createElement("div"); row.className = "file-item";
      const info = document.createElement("div");
      const name = document.createElement("div"); name.className = "file-name"; name.textContent = file.name;
      const meta = document.createElement("div"); meta.className = "file-meta";
      meta.textContent = `${formatBytes(file.size)} · ${new Date(file.modified).toLocaleString()}`;
      info.append(name, meta);
      const actions = document.createElement("div"); actions.className = "actions";
      const download = document.createElement("a"); download.className = "action";
      download.href = `/api/download/${encodeURIComponent(file.name)}`; download.textContent = "Download";
      const remove = document.createElement("button"); remove.className = "action delete";
      remove.textContent = "Delete"; remove.addEventListener("click", () => deleteFile(encodeURIComponent(file.name)));
      actions.append(download, remove); row.append(info, actions); fileList.append(row);
    }
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
  const response = await fetch(`/api/files/${encodedName}`, { method: "DELETE" });
  if (!response.ok) { alert("Delete failed. Please sign in and retry."); return; }
  await loadFiles();
}

refreshBtn.addEventListener("click", loadFiles);
loadFiles();
