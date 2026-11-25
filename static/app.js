const fileList = document.getElementById("file-list");
const panel = document.getElementById("chunk-panel");
const panelTitle = document.getElementById("chunk-title");
const chunkList = document.getElementById("chunk-list");
const closeBtn = document.getElementById("chunk-close");
const askForm = document.getElementById("ask-form");

async function loadFiles() {
  const res = await fetch("/api/files");
  const data = await res.json();

  fileList.innerHTML = "";
  for (const name of data.files) {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.textContent = name;
    btn.addEventListener("click", () => showChunks(name, btn));
    li.appendChild(btn);
    fileList.appendChild(li);
  }
}

async function showChunks(name, clickedButton) {
  for (const b of fileList.querySelectorAll("button")) {
    b.classList.remove("active");
  }
  clickedButton.classList.add("active");

  const res = await fetch(`/api/files/${encodeURIComponent(name)}/chunks`);
  if (!res.ok) {
    panelTitle.textContent = `Could not load ${name}`;
    chunkList.innerHTML = "";
    panel.hidden = false;
    return;
  }
  const data = await res.json();

  panelTitle.textContent = `${name} \u00b7 ${data.chunks.length} chunks`;
  chunkList.innerHTML = "";
  for (const c of data.chunks) {
    const card = document.createElement("article");
    card.className = "chunk";

    const label = document.createElement("small");
    label.textContent = `chunk ${c.chunk}`;

    const text = document.createElement("p");
    text.textContent = c.text;   // textContent, not innerHTML: PDF text is shown as plain text

    card.append(label, text);
    chunkList.appendChild(card);
  }
  panel.hidden = false;
}

closeBtn.addEventListener("click", () => {
  panel.hidden = true;
});


askForm.addEventListener("submit", (event) => {
  event.preventDefault();
});


loadFiles();