import React, { useEffect, useState } from 'react';
import { TreeView, TreeItem } from '@mui/lab';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import api from '../api';

export default function TemplateTree({ onSelectTemplate }) {
  const [sections, setSections] = useState([]);
  const [templatesMap, setTemplatesMap] = useState({});

  useEffect(() => {
    // загрузить разделы
    api.get('/sections/')
      .then(res => {
        setSections(res.data);
        // для каждого раздела поставить пустой массив
        const map = {};
        res.data.forEach(sec => { map[sec.id] = []; });
        setTemplatesMap(map);

        // загрузить шаблоны для каждого раздела
        res.data.forEach(sec => {
          api.get(`/sections/${sec.id}/templates`)
            .then(r2 => {
              setTemplatesMap(prev => ({ ...prev, [sec.id]: r2.data }));
            });
        });
      });
  }, []);

  // Построить дерево рекурсивно
  const buildTree = (nodes, parentId = null) =>
    nodes
      .filter(n => n.parent_id === parentId)
      .map(node => (
        <TreeItem key={node.id} nodeId={String(node.id)} label={node.name}>
          {templatesMap[node.id]?.map(t => (
            <TreeItem
              key={`t${t.id}`}
              nodeId={`t${t.id}`}
              label={t.name}
              onClick={() => onSelectTemplate(t)}
            />
          ))}
          {buildTree(nodes, node.id)}
        </TreeItem>
      ));

  return (
    <TreeView
      defaultCollapseIcon={<ExpandMoreIcon />}
      defaultExpandIcon={<ChevronRightIcon />}
      sx={{ flexGrow: 1 }}
    >
      {buildTree(sections)}
    </TreeView>
  );
}
