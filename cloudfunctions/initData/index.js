const cloud = require('wx-server-sdk');
   cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
   const { INDUSTRIES } = require('../_shared/seed');
   const { DEFAULT_TEMPLATES } = require('../_shared/defaultPrompts');

   exports.main = async () => {
     const db = cloud.database();
     for (const ind of INDUSTRIES) {
       const exist = await db.collection('industries').where({ code: ind.code }).count();
       if (exist.total === 0) await db.collection('industries').add({ data: { ...ind, createdAt: Date.now(), updatedAt: Date.now() } });
     }
     for (const tpl of DEFAULT_TEMPLATES) {
       const exist = await db.collection('prompt_templates').where({ type: tpl.type, identity: tpl.identity }).count();
       if (exist.total === 0) await db.collection('prompt_templates').add({ data: { ...tpl, active: true, createdAt: Date.now(), updatedAt: Date.now() } });
     }
     return { industries: INDUSTRIES.length, templates: DEFAULT_TEMPLATES.length };
   };
