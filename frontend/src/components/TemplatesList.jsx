import React, { useState, useEffect } from 'react';
import {
  Box, List, ListItemButton, ListItemText,
  TextField, Button, Typography, CssBaseline, AppBar, Toolbar
} from '@mui/material';
import api from '../api';

export default function TemplatesList() {
  const [templates, setTemplates] = useState([]);
  const [selected, setSelected] = useState(null);
  const [vars, setVars] = useState([]);
  const [ctx, setCtx] = useState({});

  useEffect(() => {
    api.get('/templates/')
       .then(r => setTemplates(r.data))
       .catch(console.error);
  }, []);

  const onSelect = (tpl) => {
    setSelected(tpl);
    api.get(`/templates/${tpl.id}/variables`)
       .then(r => {
         setVars(r.data.variables);
         const initial = {};
         r.data.variables.forEach(key => { initial[key] = ''; });
         setCtx(initial);
       })
       .catch(console.error);
  };

  const onChange = (key) => (e) => {
    setCtx(prev => ({ ...prev, [key]: e.target.value }));
  };

  const onGenerate = () => {
    api.post('/generate-adhoc', {
      template_id: selected.id,
      context: ctx
    }, { responseType: 'blob' })
      .then(res => {
        const blob = new Blob([res.data], {
          type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${selected.name}.docx`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
      })
      .catch(console.error);
  };

  return (
    <>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">DocBuilder</Typography>
        </Toolbar>
      </AppBar>
      <Box sx={{ display: 'flex', p: 2 }}>
        <Box sx={{ width: '30%', pr: 2 }}>
          <Typography variant="h6">Шаблоны</Typography>
          <List>
            {templates.map(t => (
              <ListItemButton
                key={t.id}
                selected={selected?.id === t.id}
                onClick={() => onSelect(t)}
              >
                <ListItemText primary={t.name} />
              </ListItemButton>
            ))}
          </List>
        </Box>
        <Box sx={{ flexGrow: 1, pl: 2 }}>
          {selected ? (
            <>
              <Typography variant="h6" gutterBottom>
                Параметры для «{selected.name}»
              </Typography>
              {vars.map(key => (
                <TextField
                  key={key}
                  label={key}
                  value={ctx[key]}
                  onChange={onChange(key)}
                  fullWidth
                  margin="normal"
                />
              ))}
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  onClick={onGenerate}
                  disabled={vars.length === 0}
                >
                  Сгенерировать
                </Button>
              </Box>
            </>
          ) : (
            <Typography>Выберите шаблон слева</Typography>
          )}
        </Box>
      </Box>
    </>
  );
}
