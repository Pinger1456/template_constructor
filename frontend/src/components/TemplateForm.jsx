import React, { useEffect, useState } from 'react';
import {
  Box, Typography, TextField, Button, MenuItem, Select, FormControl, InputLabel,
  IconButton, Paper
} from '@mui/material';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import DeleteIcon from '@mui/icons-material/Delete';
import api from '../api';

export default function TemplateForm({ template }) {
  const [cases, setCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState('');
  const [title, setTitle] = useState('');
  const [parameters, setParameters] = useState([{ key: '', value: '' }]);

  useEffect(() => {
    api.get('/cases/')
      .then(res => setCases(res.data))
      .catch(console.error);
  }, []);

  // При выборе существующего дела
  const handleCaseSelect = e => {
    const id = e.target.value;
    setSelectedCaseId(id);
    if (id) {
      const c = cases.find(x => x.id === id);
      setTitle(c.title);
      setParameters(c.parameters.map(p => ({ key: p.key, value: p.value })));
    } else {
      // Новый
      setTitle('');
      setParameters([{ key: '', value: '' }]);
    }
  };

  const handleParamChange = (idx, field, val) => {
    const arr = [...parameters];
    arr[idx][field] = val;
    setParameters(arr);
  };

  const addParam = () => {
    setParameters([...parameters, { key: '', value: '' }]);
  };

  const removeParam = idx => {
    setParameters(parameters.filter((_, i) => i !== idx));
  };

  // Сохранить дело (если новое) и/или сгенерировать
  const handleGenerate = async () => {
    let caseId = selectedCaseId;
    if (!caseId) {
      // создаём новое дело
      const payload = { title, parameters };
      const res = await api.post('/cases/', payload);
      caseId = res.data.id;
      setCases(prev => [...prev, res.data]);
      setSelectedCaseId(caseId);
    } else {
      // обновляем существующее дело
      await api.put(`/cases/${caseId}`, { title, parameters });
    }

    // Генерируем документ
    const resp = await api.post(
      '/generate',
      { template_id: template.id, case_id: caseId },
      { responseType: 'blob' }
    );
    // скачиваем
    const blob = new Blob([resp.data], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${template.name}.docx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        {template.name}
      </Typography>

      <FormControl fullWidth margin="normal">
        <InputLabel id="case-select-label">Дело</InputLabel>
        <Select
          labelId="case-select-label"
          value={selectedCaseId || ''}
          label="Дело"
          onChange={handleCaseSelect}
        >
          <MenuItem value="">Новое дело</MenuItem>
          {cases.map(c => (
            <MenuItem key={c.id} value={c.id}>
              {c.title}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <TextField
        label="Название дела"
        fullWidth
        margin="normal"
        value={title}
        onChange={e => setTitle(e.target.value)}
      />

      <Typography variant="subtitle1" sx={{ mt: 2 }}>
        Параметры
      </Typography>

      {parameters.map((p, idx) => (
        <Paper key={idx} sx={{ p: 2, my: 1, position: 'relative' }}>
          <IconButton
            size="small"
            sx={{ position: 'absolute', top: 4, right: 4 }}
            onClick={() => removeParam(idx)}
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
          <TextField
            label="Ключ"
            value={p.key}
            onChange={e => handleParamChange(idx, 'key', e.target.value)}
            sx={{ mb: 1 }}
            fullWidth
          />
          <TextField
            label="Значение"
            value={p.value}
            onChange={e => handleParamChange(idx, 'value', e.target.value)}
            fullWidth
          />
        </Paper>
      ))}

      <Button
        startIcon={<AddCircleIcon />}
        onClick={addParam}
        sx={{ mt: 1 }}
      >
        Добавить параметр
      </Button>

      <Box sx={{ mt: 4 }}>
        <Button variant="contained" onClick={handleGenerate}>
          Сгенерировать документ
        </Button>
      </Box>
    </Box>
  );
}
