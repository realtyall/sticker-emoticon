(function () {
  // API 모달
  const apiModal = document.getElementById('apiModal');
  const apiSettingsBtn = document.getElementById('apiSettingsBtn');
  const apiKeyInput = document.getElementById('apiKeyInput');
  const apiConfirmBtn = document.getElementById('apiConfirmBtn');
  const apiCancelBtn = document.getElementById('apiCancelBtn');
  const validationStatus = document.getElementById('validationStatus');
  const validationMessage = document.getElementById('validationMessage');
  const saveOptionRadios = document.querySelectorAll('input[name="saveOption"]');

  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const previewWrap = document.getElementById('previewWrap');
  const previewImg = document.getElementById('previewImg');
  const resetBtn = document.getElementById('resetBtn');
  const generateBtn = document.getElementById('generateBtn');

  const uploadSection = document.getElementById('uploadSection');
  const loadingSection = document.getElementById('loadingSection');
  const loadingMsg = document.getElementById('loadingMsg');
  const errorSection = document.getElementById('errorSection');
  const errorMsg = document.getElementById('errorMsg');
  const retryBtn = document.getElementById('retryBtn');
  const resultSection = document.getElementById('resultSection');

  const gridImg = document.getElementById('gridImg');
  const gridDownloadBtn = document.getElementById('gridDownloadBtn');
  const zipDownloadBtn = document.getElementById('zipDownloadBtn');
  const stickerGrid = document.getElementById('stickerGrid');
  const stickerCount = document.getElementById('stickerCount');
  const newBtn = document.getElementById('newBtn');

  const stickerSelector = document.getElementById('stickerSelector');
  const stickerCountSlider = document.getElementById('stickerCountSlider');
  const sliderValue = document.getElementById('sliderValue');

  let selectedFile = null;
  let currentApiKey = null;

  // API 키 관리
  function loadApiKey() {
    const saved = localStorage.getItem('gemini_api_key');
    if (saved) {
      currentApiKey = saved;
    }
  }

  function showApiModal() {
    apiKeyInput.value = currentApiKey || '';
    validationStatus.style.display = 'none';
    apiConfirmBtn.disabled = false;
    apiModal.classList.remove('hidden');
    apiKeyInput.focus();
  }

  function hideApiModal() {
    apiModal.classList.add('hidden');
    validationStatus.style.display = 'none';
  }

  function saveApiKey(apiKey, persistent) {
    currentApiKey = apiKey;
    if (persistent) {
      localStorage.setItem('gemini_api_key', apiKey);
    }
    hideApiModal();
  }

  apiSettingsBtn.addEventListener('click', showApiModal);
  apiCancelBtn.addEventListener('click', hideApiModal);

  async function validateAndSaveApiKey() {
    const apiKey = apiKeyInput.value.trim();
    if (!apiKey) {
      validationStatus.classList.remove('success');
      validationStatus.classList.add('error');
      validationMessage.textContent = 'API 키를 입력해주세요.';
      validationStatus.style.display = 'block';
      return;
    }

    apiConfirmBtn.disabled = true;
    validationStatus.classList.remove('success', 'error');
    validationMessage.textContent = '검증 중...';
    validationStatus.style.display = 'block';

    try {
      const response = await fetch('/api/validate-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey }),
      });

      const data = await response.json();

      if (data.valid) {
        validationStatus.classList.add('success');
        validationStatus.classList.remove('error');
        validationMessage.textContent = data.message;

        setTimeout(() => {
          const saveOption = document.querySelector('input[name="saveOption"]:checked').value;
          const persistent = saveOption === 'persistent';
          saveApiKey(apiKey, persistent);
        }, 800);
      } else {
        validationStatus.classList.add('error');
        validationStatus.classList.remove('success');
        validationMessage.textContent = data.error || '유효하지 않은 API 키입니다.';
        apiConfirmBtn.disabled = false;
      }
    } catch (err) {
      validationStatus.classList.add('error');
      validationStatus.classList.remove('success');
      validationMessage.textContent = '검증 중 오류가 발생했습니다: ' + err.message;
      apiConfirmBtn.disabled = false;
    }
  }

  apiConfirmBtn.addEventListener('click', validateAndSaveApiKey);

  apiKeyInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      apiConfirmBtn.click();
    }
  });

  // 초기 로드
  loadApiKey();

  function showSection(section) {
    [uploadSection, loadingSection, errorSection, resultSection].forEach(s => {
      s.style.display = 'none';
    });
    section.style.display = section === uploadSection ? 'flex' : 'block';
    if (section === resultSection) section.style.display = 'flex';
  }

  // 드래그 앤 드롭
  dropZone.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('dragover', e => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
  });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) setFile(file);
  });
  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) setFile(fileInput.files[0]);
  });

  function setFile(file) {
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = e => {
      previewImg.src = e.target.result;
      dropZone.style.display = 'none';
      previewWrap.style.display = 'flex';
      stickerSelector.style.display = 'flex';
      generateBtn.disabled = false;
    };
    reader.readAsDataURL(file);
  }

  resetBtn.addEventListener('click', () => {
    selectedFile = null;
    fileInput.value = '';
    previewImg.src = '';
    dropZone.style.display = '';
    previewWrap.style.display = 'none';
    stickerSelector.style.display = 'none';
    generateBtn.disabled = true;
  });

  // 슬라이더 값 변경
  stickerCountSlider.addEventListener('input', () => {
    sliderValue.textContent = stickerCountSlider.value;
  });

  // 생성 버튼
  generateBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    if (!currentApiKey) {
      alert('먼저 API 키를 설정해주세요.');
      showApiModal();
      return;
    }

    showSection(loadingSection);
    loadingMsg.textContent = 'AI가 스티커를 생성하고 있습니다...';

    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('sticker_count', stickerCountSlider.value);
    formData.append('api_key', currentApiKey);

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        showError(data.error || '알 수 없는 오류가 발생했습니다.');
        return;
      }

      loadingMsg.textContent = '스티커를 분할하는 중...';
      renderResult(data);
    } catch (err) {
      showError('서버와 통신 중 오류가 발생했습니다: ' + err.message);
    }
  });

  function renderResult(data) {
    gridImg.src = data.grid_preview_url;
    gridDownloadBtn.href = data.grid_download_url;
    zipDownloadBtn.href = `/api/download/all/${data.session_id}`;

    stickerGrid.innerHTML = '';
    stickerCount.textContent = `(${data.stickers.length}개)`;

    data.stickers.forEach(sticker => {
      const item = document.createElement('div');
      item.className = 'sticker-item';

      const img = document.createElement('img');
      img.src = sticker.preview_url;
      img.alt = sticker.name;
      img.loading = 'lazy';

      const link = document.createElement('a');
      link.href = sticker.download_url;
      link.download = sticker.name;
      link.textContent = '다운로드';

      item.appendChild(img);
      item.appendChild(link);
      stickerGrid.appendChild(item);
    });

    showSection(resultSection);
  }

  function showError(msg) {
    errorMsg.textContent = msg;
    showSection(errorSection);
  }

  retryBtn.addEventListener('click', () => showSection(uploadSection));
  newBtn.addEventListener('click', () => {
    resetBtn.click();
    showSection(uploadSection);
  });
})();
