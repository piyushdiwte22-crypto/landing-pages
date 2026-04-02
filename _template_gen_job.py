import json, sys

# SET THESE PER SESSION:
SESSION = '/sessions/REPLACE_ME/'  # Update to current session path
DATE_STR = "DD Month YYYY"         # Update to current date

def gen(cfg):
    """Generate build_job.js from config dict. Supports LP and non-LP CL formats."""
    j = cfg
    def esc(s):
        return s.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')

    cl_body = ','.join(['"'+esc(p)+'"' for p in j['cl_body']])
    ps = ','.join(['"'+esc(s)+'"' for s in j['prof_skills']])
    ts = ','.join(['"'+esc(s)+'"' for s in j['tech_skills']])

    def bullets_js(name, arr):
        return 'const '+name+'=['+','.join(['"'+esc(b)+'"' for b in arr])+'];'

    b1 = bullets_js('B1', j['b_patrolapart'])
    b2 = bullets_js('B2', j['b_hamilton'])
    b3 = bullets_js('B3', j['b_scape'])
    b4 = bullets_js('B4', j['b_hiranya'])
    b5 = bullets_js('B5', j['b_oyo'])
    b6 = bullets_js('B6', j['b_codecamp'])

    lp_url = j.get('lp_url', '')
    is_lp = bool(lp_url)
    addr_name = j.get('addressee', 'Hiring Team')
    salutation = f'Dear {addr_name},' if addr_name != 'Hiring Team' else 'Dear Hiring Manager,'

    # Email line in addressee block
    if j.get('co_email'):
        email_line = f'cl.push(new Pa({{spacing:{{before:0,after:180}},children:[hl("{j["co_email"]}","mailto:{j["co_email"]}",23)]}}));'
    else:
        email_line = 'cl.push(new Pa({spacing:{before:0,after:180},children:[]}));'

    # CL contact line (LP vs standard)
    if is_lp:
        cl_contact_js = f'cl.push(new Pa({{alignment:A.LEFT,spacing:{{before:160,after:220}},children:[new T({{text:LOC+"   |   +61 415 122 028   |   ",font:"Calibri",size:19,color:NB}}),hl("Piyushdiwte22@gmail.com","mailto:piyushdiwte22@gmail.com",19),new T({{text:"   |   ",font:"Calibri",size:19,color:NB}}),hl("My Showcase","{esc(lp_url)}",19)]}}));'
    else:
        cl_contact_js = 'cl.push(new Pa({alignment:A.LEFT,spacing:{before:160,after:220},children:[new T({text:LOC+"   |   +61 415 122 028   |   ",font:"Calibri",size:19,color:NB}),hl("Piyushdiwte22@gmail.com","mailto:piyushdiwte22@gmail.com",19),new T({text:"   |   ",font:"Calibri",size:19,color:NB}),hl("CapturedByPiyush.com","https://www.capturedbypiyush.com",19),new T({text:"   |   ",font:"Calibri",size:19,color:NB}),hl("My Vertical Work","https://linktr.ee/Piyush_Diwte",19)]}));'

    # Resume contact line (LP vs standard)
    if is_lp:
        resume_contact_js = f're.push(new Pa({{alignment:A.CENTER,spacing:{{before:0,after:45}},children:[new T({{text:LOC+"   |   +61 415 122 028   |   ",font:"Calibri",size:17,color:NB}}),hl("Piyushdiwte22@gmail.com","mailto:piyushdiwte22@gmail.com",17),new T({{text:"   |   ",font:"Calibri",size:17,color:NB}}),hl("My Showcase","{esc(lp_url)}",17)]}}));'
    else:
        resume_contact_js = 're.push(new Pa({alignment:A.CENTER,spacing:{before:0,after:45},children:[new T({text:LOC+"   |   +61 415 122 028   |   ",font:"Calibri",size:17,color:NB}),hl("Piyushdiwte22@gmail.com","mailto:piyushdiwte22@gmail.com",17),new T({text:"   |   ",font:"Calibri",size:17,color:NB}),hl("CapturedByPiyush.com","https://www.capturedbypiyush.com",17),new T({text:"   |   ",font:"Calibri",size:17,color:NB}),hl("My Vertical Work","https://linktr.ee/Piyush_Diwte",17)]}));'

    # CL portfolio section (LP = charming paragraph with hyperlinked LP ref, standard = bullets + website)
    # LOCKED Day 11: ALL LP jobs use SINGLE showcase link. For LP+PS, visa text goes in cl_pf_after as plain text.
    has_ps = bool(j.get('ps_line') or j.get('ps_before'))
    if is_lp:
        pf_before = esc(j.get('cl_pf_before', 'The best way to evaluate a content creator is to see their work. I put together '))
        pf_link = esc(j.get('cl_pf_link', 'a portfolio page for this role'))
        pf_after = esc(j.get('cl_pf_after', ' with video samples, results, and the kind of content I would produce for your team.'))
        # Single hyperlink for ALL LP jobs (LP-only and LP+PS alike)
        # For LP+PS jobs, cl_pf_after must include the visa text as plain text
        cl_portfolio_js = f'cl.push(new Pa({{alignment:A.JUSTIFIED,spacing:{{before:0,after:180}},children:[new T({{text:"{pf_before}",font:"Calibri",size:23,color:NB}}),hl("{pf_link}","{esc(lp_url)}",23),new T({{text:"{pf_after}",font:"Calibri",size:23,color:NB}})]}}))'
        cl_pf_var = ''
    else:
        cl_pf = ','.join(['{text:"'+esc(p['text'])+'",url:"'+p['url']+'"}' for p in j['cl_portfolio']])
        cl_pf_var = f'const CL_PF=[{cl_pf}];'
        ws = esc(j.get('cl_website_sentence', 'You can explore more of my work on '))
        cl_portfolio_js = (
            'cl.push(new Pa({alignment:A.LEFT,spacing:{before:0,after:100},children:[new T({text:"A few examples of my work:",font:"Calibri",size:23,color:NB})]}));\n'
            'CL_PF.forEach(function(l){cl.push(new Pa({numbering:{reference:"cb",level:0},spacing:{before:50,after:50},children:[hl(l.text,l.url,23)]}));});\n'
            f'cl.push(new Pa({{alignment:A.JUSTIFIED,spacing:{{before:120,after:180}},children:[new T({{text:"{ws}",font:"Calibri",size:23,color:NB}}),hl("my website","https://www.capturedbypiyush.com",23),new T({{text:" or browse ",font:"Calibri",size:23,color:NB}}),hl("my vertical work","https://linktr.ee/Piyush_Diwte",23),new T({{text:" for a closer look at my content across platforms.",font:"Calibri",size:23,color:NB}})]}}));'
        )

    # PS line — only used as SEPARATE paragraph for non-LP jobs or LP jobs without ps_link_text
    # For LP + PS jobs, the PS is already merged into the portfolio paragraph above
    ps_line_js = ''
    if has_ps and not is_lp:
        if j.get('ps_line'):
            ps_line_js = f'cl.push(new Pa({{alignment:A.JUSTIFIED,spacing:{{before:0,after:180}},children:[new T({{text:"P.S. {esc(j["ps_line"])}",font:"Calibri",size:23,italics:true,color:NB}})]}}))'

    # CL footer (LP vs standard)
    if is_lp:
        cl_footer_children = f'tr("Melbourne, VIC   |   +61 415 122 028   |   ",{{size:17,color:WH}}),hlw("Piyushdiwte22@gmail.com","mailto:piyushdiwte22@gmail.com",17),tr("   |   ",{{size:17,color:WH}}),hlw("My Showcase","{esc(lp_url)}",17)'
    else:
        cl_footer_children = 'tr("Melbourne, VIC   |   +61 415 122 028   |   ",{size:17,color:WH}),hlw("Piyushdiwte22@gmail.com","mailto:piyushdiwte22@gmail.com",17),tr("   |   ",{size:17,color:WH}),hlw("CapturedByPiyush.com","https://www.capturedbypiyush.com",17)'

    # Resume footer (LP vs standard)
    if is_lp:
        resume_footer_children = f'tr("Melbourne, VIC   |   +61 415 122 028   |   ",{{size:17,color:WH}}),hlw("Piyushdiwte22@gmail.com","mailto:piyushdiwte22@gmail.com",17),tr("   |   ",{{size:17,color:WH}}),hlw("My Showcase","{esc(lp_url)}",17)'
    else:
        resume_footer_children = 'tr("Melbourne, VIC   |   +61 415 122 028   |   ",{size:17,color:WH}),hlw("Piyushdiwte22@gmail.com","mailto:piyushdiwte22@gmail.com",17),tr("   |   ",{size:17,color:WH}),hlw("CapturedByPiyush.com","https://www.capturedbypiyush.com",17),tr("   |   ",{size:17,color:WH}),hlw("My Vertical Work","https://linktr.ee/Piyush_Diwte",17)'

    # Use the original f-string approach with {{ }} escaping for the full JS
    js = f'''const{{Document:D,Packer:P,Paragraph:Pa,TextRun:T,Table:Tb,TableRow:TR,TableCell:TC,AlignmentType:A,WidthType:W,BorderStyle:B,ShadingType:S,LevelFormat:L,ExternalHyperlink:E,UnderlineType:U}}=require('docx');
const fs=require('fs');
const JT_UP="{esc(j['jt_up'])}",JT_D="{esc(j['jt_d'])}",CO="{esc(j['company'])}",ADDR="{esc(addr_name)}",RE="Re: {esc(j['jt_d'])}",DATE="{DATE_STR}",PRE="{j['prefix']}",LOC="{j.get('location','Melbourne, VIC')}";
const SUM="{esc(j['summary'])}";
const CL=[{cl_body}];
const CL_CL="{esc(j['cl_closing'])}";
{cl_pf_var}
const PS=[{ps}];
const TS=[{ts}];
{b1}
{b2}
{b3}
{b4}
{b5}
{b6}
const SP={{bulletBefore:2,bulletAfter:2,sectionBefore:40,ruleAfter:10,jobTitleBefore:20,companyAfter:8,footerSpacer:10}};
const DB="4A2800",WB="7C4A1E",NB="1A1A2E",NK="0D0D0D",LB="0563C1",WH="FFFFFF",TH="C8B8A8";

function hl(t,u,s){{return new E({{link:u,children:[new T({{text:t,font:"Calibri",size:s||17,color:LB,underline:{{type:U.NONE}}}})]}})}}
function hlw(t,u,s){{return new E({{link:u,children:[new T({{text:t,font:"Calibri",size:s||17,color:WH,underline:{{type:U.NONE}}}})]}})}}
function tr(t,o={{}}){{var r={{text:t,font:"Calibri",size:o.size!==undefined?o.size:20,bold:o.bold||false,color:o.color||NB,underline:{{type:U.NONE}}}};if(o.characterSpacing!==undefined)r.characterSpacing=o.characterSpacing;return new T(r)}}
function bp(t,n,o={{}}){{return new Pa({{numbering:{{reference:n,level:0}},spacing:{{before:o.before||SP.bulletBefore,after:o.after||SP.bulletAfter}},alignment:A.LEFT,children:[tr(t,{{size:o.size||20}})]}})}}
function sh(t){{return[new Pa({{alignment:A.LEFT,spacing:{{before:SP.sectionBefore,after:0}},children:[tr(t,{{size:21,bold:true,color:WB}})]}}),new Pa({{spacing:{{before:0,after:SP.ruleAfter}},border:{{bottom:{{style:B.SINGLE,size:8,color:WB,space:1}}}},children:[]}})]}}
function nB(){{return{{top:{{style:B.NONE,size:0,color:"FFFFFF"}},bottom:{{style:B.NONE,size:0,color:"FFFFFF"}},left:{{style:B.NONE,size:0,color:"FFFFFF"}},right:{{style:B.NONE,size:0,color:"FFFFFF"}},insideH:{{style:B.NONE,size:0,color:"FFFFFF"}},insideV:{{style:B.NONE,size:0,color:"FFFFFF"}}}}}}
function nBC(){{return{{top:{{style:B.NONE,size:0,color:"FFFFFF"}},bottom:{{style:B.NONE,size:0,color:"FFFFFF"}},left:{{style:B.NONE,size:0,color:"FFFFFF"}},right:{{style:B.NONE,size:0,color:"FFFFFF"}}}}}}
function fb(w){{
  var r1=new Pa({{alignment:A.CENTER,spacing:{{before:0,after:0}},children:[{resume_footer_children}]}});
  return new Tb({{width:{{size:w,type:W.DXA}},columnWidths:[w],borders:nB(),rows:[new TR({{children:[new TC({{width:{{size:w,type:W.DXA}},shading:{{fill:DB,type:S.CLEAR}},borders:nBC(),margins:{{top:120,bottom:120,left:220,right:220}},children:[r1]}})]}})]}}); }}
function fbCL(w){{
  var r1=new Pa({{alignment:A.CENTER,spacing:{{before:0,after:0}},children:[{cl_footer_children}]}});
  return new Tb({{width:{{size:w,type:W.DXA}},columnWidths:[w],borders:nB(),rows:[new TR({{children:[new TC({{width:{{size:w,type:W.DXA}},shading:{{fill:DB,type:S.CLEAR}},borders:nBC(),margins:{{top:120,bottom:120,left:220,right:220}},children:[r1]}})]}})]}}); }}
function je(ti,co,ld,bu){{
  var i=[];
  i.push(new Pa({{alignment:A.LEFT,spacing:{{before:SP.jobTitleBefore,after:0}},children:[tr(ti,{{size:21,bold:true,color:NB}})]}}));
  i.push(new Pa({{alignment:A.LEFT,spacing:{{before:0,after:SP.companyAfter}},children:[tr(co,{{size:20,bold:true,color:WB}}),tr(ld,{{size:20}})]}}));
  bu.forEach(function(b){{i.push(bp(b,"rb"))}});return i; }}
function sg(items,w){{
  var c=3,cw=Math.floor(w/c),rows=[];
  for(var i=0;i<items.length;i+=c){{var cells=[];for(var j=0;j<c;j++){{cells.push(new TC({{width:{{size:cw,type:W.DXA}},borders:nBC(),margins:{{top:15,bottom:15,left:40,right:40}},children:[new Pa({{spacing:{{before:0,after:0}},children:items[i+j]?[tr("\\u2022 "+items[i+j],{{size:19}})]:[]}})]}}))}};rows.push(new TR({{children:cells}}))}}
  return new Tb({{width:{{size:w,type:W.DXA}},columnWidths:[cw,cw,cw],borders:nB(),rows:rows}}); }}

var nc=[{{reference:"rb",levels:[{{level:0,format:L.BULLET,text:"\\u2022",alignment:A.LEFT,style:{{paragraph:{{indent:{{left:420,hanging:210}}}}}}}}]}},{{reference:"cb",levels:[{{level:0,format:L.BULLET,text:"\\u2022",alignment:A.LEFT,style:{{paragraph:{{indent:{{left:480,hanging:240}}}}}}}}]}}];

var CW=9412,CBW=5835,cl=[];
cl.push(new Tb({{width:{{size:CBW,type:W.DXA}},columnWidths:[CBW],borders:nB(),rows:[new TR({{children:[new TC({{width:{{size:CBW,type:W.DXA}},shading:{{fill:DB,type:S.CLEAR}},borders:nBC(),margins:{{top:120,bottom:120,left:220,right:220}},children:[new Pa({{alignment:A.LEFT,spacing:{{before:0,after:0}},children:[new T({{text:"PIYUSH DIWTE   |   "+JT_D,font:"Calibri",size:20,bold:true,color:WH}})]}})]}})]}})]}}));
{cl_contact_js}
cl.push(new Pa({{spacing:{{before:0,after:180}},children:[new T({{text:DATE,font:"Calibri",size:23,color:NB}})]}}));
cl.push(new Pa({{spacing:{{before:0,after:0}},children:[new T({{text:ADDR,font:"Calibri",size:23,color:NB}})]}}));
cl.push(new Pa({{spacing:{{before:0,after:0}},children:[new T({{text:CO,font:"Calibri",size:23,color:NB}})]}}));
{email_line}
cl.push(new Pa({{spacing:{{before:0,after:180}},children:[new T({{text:RE,font:"Calibri",size:23,bold:true,color:NB}})]}}));
cl.push(new Pa({{spacing:{{before:0,after:180}},children:[new T({{text:"{esc(salutation)}",font:"Calibri",size:23,color:NB}})]}}));
CL.forEach(function(t){{cl.push(new Pa({{alignment:A.JUSTIFIED,spacing:{{before:0,after:180}},children:[new T({{text:t,font:"Calibri",size:23,color:NB}})]}}));}});
{cl_portfolio_js};
{ps_line_js};
cl.push(new Pa({{alignment:A.JUSTIFIED,spacing:{{before:180,after:180}},children:[new T({{text:CL_CL,font:"Calibri",size:23,color:NB}})]}}));
cl.push(new Pa({{alignment:A.LEFT,spacing:{{before:0,after:180}},children:[new T({{text:"Thank you for your time and consideration.",font:"Calibri",size:23,color:NB}})]}}));
cl.push(new Pa({{spacing:{{before:0,after:80}},children:[new T({{text:"Warm regards,",font:"Calibri",size:23,color:NB}})]}}));
cl.push(new Pa({{spacing:{{before:0,after:0}},children:[new T({{text:"Piyush Diwte",font:"Calibri",size:23,bold:true,color:NB}})]}}));
cl.push(new Pa({{spacing:{{before:0,after:240}},children:[]}}));
cl.push(fbCL(CW));
var clDoc=new D({{numbering:{{config:nc}},sections:[{{properties:{{page:{{size:{{width:11906,height:16838}},margin:{{top:1134,bottom:1134,left:1247,right:1247}}}}}},children:cl}}]}});

var RW=9638,re=[];
re.push(new Pa({{alignment:A.CENTER,spacing:{{before:0,after:20}},children:[new T({{text:"PIYUSH DIWTE",font:"Calibri",size:64,bold:true,color:NK}})]}}));
re.push(new Tb({{width:{{size:RW,type:W.DXA}},columnWidths:[1607,6424,1607],borders:nB(),rows:[new TR({{children:[new TC({{width:{{size:1607,type:W.DXA}},shading:{{fill:DB,type:S.CLEAR}},borders:nBC(),margins:{{top:30,bottom:30,left:0,right:0}},children:[new Pa({{spacing:{{before:0,after:0}},children:[]}})]}})
,new TC({{width:{{size:6424,type:W.DXA}},shading:{{fill:WB,type:S.CLEAR}},borders:nBC(),margins:{{top:30,bottom:30,left:0,right:0}},children:[new Pa({{spacing:{{before:0,after:0}},children:[]}})]}})
,new TC({{width:{{size:1607,type:W.DXA}},shading:{{fill:DB,type:S.CLEAR}},borders:nBC(),margins:{{top:30,bottom:30,left:0,right:0}},children:[new Pa({{spacing:{{before:0,after:0}},children:[]}})]}})]}})]}}));
re.push(new Pa({{spacing:{{before:0,after:50}},children:[]}}));
re.push(new Pa({{alignment:A.CENTER,spacing:{{before:0,after:45}},children:[new T({{text:JT_UP,font:"Calibri",size:20,bold:true,color:WB,characterSpacing:100}})]}}));
{resume_contact_js}
re.push(new Pa({{spacing:{{before:0,after:90}},border:{{bottom:{{style:B.SINGLE,size:4,color:TH,space:1}}}},children:[]}}));
re.push(...sh("PROFESSIONAL SUMMARY"));
re.push(new Pa({{alignment:A.JUSTIFIED,spacing:{{before:0,after:0}},children:[new T({{text:SUM,font:"Calibri",size:20,color:NB}})]}}));
re.push(...sh("PROFESSIONAL EXPERIENCE"));
re.push(...je("Digital Content Creator and Manager","Patrolapart and Navarapart","   |   Hybrid (VIC)   |   April 2025 to Present",B1));
re.push(...je("Digital Content Creator and Manager","Hamilton Island","   |   Hybrid (VIC and QLD)   |   July 2024 to April 2025",B2));
re.push(...je("Digital Content Coordinator","Scape Australia","   |   Hybrid (VIC, NSW, QLD, SA)   |   April 2023 to July 2024",B3));
re.push(...je("Digital Content Creator","Hiranya Resort","   |   Contract   |   Aurangabad, Maharashtra   |   March 2020 to January 2023",B4));
re.push(...je("Digital Content Creator and Manager","OYO, Taj Hotels, Sula Vineyards","   |   Contract   |   Aurangabad, Maharashtra   |   March 2020 to January 2023",B5));
re.push(...je("Volunteer, Head Teacher and Content Creator","Code Camp","   |   Melbourne, VIC   |   February 2023 to Present",B6));
re.push(...sh("PROFESSIONAL SKILLS"));re.push(sg(PS,RW));
re.push(...sh("TECHNICAL SKILLS"));re.push(sg(TS,RW));
re.push(...sh("EDUCATION"));
re.push(new Pa({{spacing:{{before:30,after:0}},children:[tr("Master of Media and Communication",{{size:21,bold:true}})]}}));
re.push(new Pa({{spacing:{{before:0,after:20}},children:[tr("RMIT University, Melbourne, VIC",{{size:20}})]}}));
re.push(new Pa({{spacing:{{before:30,after:0}},children:[tr("Bachelor of Animation and Post-Production",{{size:21,bold:true}})]}}));
re.push(new Pa({{spacing:{{before:0,after:20}},children:[tr("BAMU University, Aurangabad, India",{{size:20}})]}}));
re.push(...sh("CERTIFICATIONS"));
["CASA Remote Pilot Licence (RePL) \\u2014 Licensed Drone Operator","Adobe Premiere Pro Professional Certificate","Social Media Marketing Certificate","Working with Children Check (VIC)"].forEach(function(c){{re.push(bp(c,"rb",{{before:8,after:8}}))}});
re.push(new Pa({{spacing:{{before:0,after:SP.footerSpacer}},children:[]}}));
re.push(fb(RW));
var reDoc=new D({{numbering:{{config:nc}},sections:[{{properties:{{page:{{size:{{width:11906,height:16838}},margin:{{top:680,bottom:680,left:1134,right:1134}}}}}},children:re}}]}});
var O='{SESSION}';
Promise.all([P.toBuffer(clDoc).then(function(b){{fs.writeFileSync(O+PRE+'_CL.docx',b);console.log('CL written')}}),P.toBuffer(reDoc).then(function(b){{fs.writeFileSync(O+PRE+'_Resume.docx',b);console.log('Resume written')}})]).then(function(){{console.log('Done')}}).catch(function(e){{console.error(e);process.exit(1)}});
'''
    with open(SESSION+'build_job.js','w') as f:
        f.write(js)
    print(f"{cfg['prefix']} script written OK")
