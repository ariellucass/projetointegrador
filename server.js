// server.js

// 1. Modulos utilizados
const express = require('express');
const path = require('path');
const session = require('express-session');
const { Pool } = require('pg');
const bcrypt = require('bcrypt'); 
const { spawn } = require('child_process');
const app = express();
const PORT = process.env.PORT || 3000;
const crypto = require('crypto')


//--Variavel tamanho senha  aleatoria
const tamanhoDaSenha = 10;


// 2. Middlewares
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));
app.use(session(
{
    secret: process.env.SESSION_SECRET || 'chaveSegura123',
    resave: false,
    saveUninitialized: false,
cookie:
    {
        httpOnly: true,
        secure: false, // true se usar HTTPS
        maxAge: 1000 * 60 * 60 // 1 hora
    }
}));

// 3. Conexão PostgreSQL
const pool = new Pool(
{
    user: process.env.DB_USER || 'lucas',
    host: process.env.DB_HOST || 'localhost',
    database: process.env.DB_NAME || 'projeto',
    password: process.env.DB_PASSWORD || '18059829',
    port: process.env.DB_PORT || 5432,
});

pool.connect(err =>
{
    if (err)
    {
        console.error('Falha ao conectar com o PostgreSQL:', err.stack);
    }
    else
    {
        console.log('Conectado ao PostgreSQL.');
    }
});

// 4. Middleware de verificação de login
function verificarLogin(req, res, next)
{
    if (req.session.user)
    {
        next();
    }
    else
    {
        res.redirect('/login');
    }
}

// 5. Rotas

// Tela de login
app.get('/login', (req, res) =>
{
    res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

// Processamento do login
app.post('/login', async (req, res) =>
{
    const { login, senha } = req.body;

    if (!login || !senha)
    {
        return res.status(400).send('Usuário e senha obrigatórios.');
    }

    try
    {
        const query = 'SELECT * FROM usuarios WHERE login = $1';
        const result = await pool.query(query, [login]);

        if (result.rows.length === 0)
        {
            return res.send('<h1>Login inválido</h1><a href="/login">Tentar novamente</a>');
        }

        const user = result.rows[0];
        const senhaValida = await bcrypt.compare(senha, user.senha); //--Validacao Segura da senha

        if (!senhaValida)
        {
            return res.send('<h1>Login inválido</h1><a href="/login">Tentar novamente</a>');
        }

        req.session.user = user.login;
        res.redirect('/');
     }
     catch (err)
     {
         console.error('Erro ao autenticar:', err);
         res.status(500).send('Erro interno.');
     }
});

// Logout
app.get('/logout', (req, res) =>
{
    req.session.destroy(err =>
    {
        if (err) console.error('Erro ao destruir sessão:', err);
        res.redirect('/login');
    });
});

// Página principal protegida
app.get('/', verificarLogin, (req, res) =>
{
    res.sendFile(path.join(__dirname, 'public', 'main.html'));
});

// Cadastro de morador
app.post('/cadastrar', verificarLogin, async (req, res) =>
{
    const { nome, telefone, bloco, apartamento } = req.body;
    if (!nome || !telefone || !bloco || !apartamento)
    {
        return res.status(400).send('<h1>Erro</h1><p>Informe todos os dados obrigatórios.</p><a href="/">Voltar</a>');
    }

    try
    {
        const checkQuery = 'SELECT COUNT(*) FROM morador WHERE telefone = $1 AND bloco = $2 AND apartamento = $3';
        const checkResult = await pool.query(checkQuery, [telefone, bloco, apartamento]);
        const existe = parseInt(checkResult.rows[0].count) > 0;

        if (existe)
        {
            return res.status(409).send('<h1>Atenção</h1><p>Já existe esse morador.</p><a href="/">Voltar</a>');
        }
        const insertQuery = 'INSERT INTO morador (nome, telefone, bloco, apartamento) VALUES ($1, $2, $3, $4)';
        await pool.query(insertQuery, [nome, telefone, bloco, apartamento]);
        const novaSenha = gerarSenha(tamanhoDaSenha); // Funcao para gerar senha aleatoria;;
        const CriarPJSIP = spawn('python3.11', ['InclusaoRamais.py',telefone,nome,novaSenha]); // Inclusao dos ramais no PJSIP
        const ReiniciarPJSIP = spawn('python3.11', ['reiniciarpjsip.py']); // Reiniciar modulo

        res.send(`<h1>Sucesso</h1><p>Morador <strong>${nome}</strong> cadastrado. Numero: ${telefone} Senha de acesso: ${novaSenha} </p><a href="/">Voltar</a>`);
    }

    catch (err)
    {
        console.error('Erro no cadastro:', err);
        res.status(500).send('<h1>Erro</h1><p>Erro ao cadastrar.</p><a href="/">Voltar</a>');
    }
});

//Cadastro Usuarios

app.post('/cadastrousuario', verificarLogin, async (req, res) =>
{
    const { login, senha } = req.body;
    if (!login || !senha)
    {
        return res.status(400).send('<h1>Erro</h1><p>Login e senha são obrigatórios.</p><a href="/cadastrousuario">Voltar</a>');
    }

    try
    {
        const hash = await bcrypt.hash(senha, 10); // 🔐 Criptografa a senha
        const existeQuery = 'SELECT * FROM usuarios WHERE login = $1';
        const existe = await pool.query(existeQuery, [login]);
        if (existe.rows.length > 0)
        {
            return res.status(409).send('<h1>Erro</h1><p>Usuário já existe.</p><a href="/cadastrousuario">Voltar</a>');
        }

        const insertQuery = 'INSERT INTO usuarios (login, senha) VALUES ($1, $2)';
        await pool.query(insertQuery, [login, hash]);
        res.send('<h1>Usuário cadastrado com sucesso!</h1><a href="/">Voltar</a>');
    }

    catch (err)
    {
        console.error('Erro ao registrar usuário:', err);
        res.status(500).send('<h1>Erro interno</h1><a href="/">Voltar</a>');
    }
});

// Consulta por data

app.post('/consultar', verificarLogin, async (req, res) =>
{
    const { data_inicio, data_fim } = req.body;
    if (!data_inicio || !data_fim)
    {
        // Retorna JSON para o front-end
        return res.status(400).json({ error: 'Datas de início e fim são obrigatórias.' });
    }

    try
    {
        const query = `SELECT nomeramal, ramalprincipal, ramaldestino, contexto,
             TO_CHAR(ligacaorealizada, 'DD/MM/YYYY HH24:MI') AS ligacaorealizada,
             TO_CHAR(ligacaofinal, 'DD/MM/YYYY HH24:MI') AS ligacaofinal,
             duracao
             FROM cdr
             WHERE ligacaorealizada BETWEEN $1 AND $2
             ORDER BY ligacaorealizada DESC`; //Query da consulta

        const values = [data_inicio, data_fim];
        const { rows } = await pool.query(query, values);

        // Retorna os dados como JSON
        res.json(rows);

    }

    catch (err)
    {
        console.error('Erro na consulta:', err);
        // Retorna JSON para o front-end em caso de erro
        res.status(500).json({ error: 'Não foi possível consultar os dados.' });
    }
});

function gerarSenha(tamanho)
{
    const caracteres = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let senha = '';
    for (let i = 0; i < tamanho; i++)
    {
        const indiceAleatorio = crypto.randomInt(0, caracteres.length);
        senha += caracteres[indiceAleatorio];
    }

    return senha;
}


// 6. Inicia o servidor
app.listen(PORT, () =>
{
    console.log(` Servidor rodando em http://localhost:${PORT}`);
});
