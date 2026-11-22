% =====================================================================
% ARQUIVO PROVISORIO -- NAO E O webmedia.cls OFICIAL.
% Serve apenas para compilar localmente. Antes da entrega, substitua por
% webmedia.cls do template oficial (Overleaf):
%   https://www.overleaf.com/latex/templates/webmedia-template/ckjcbscxjjjh
% O webmedia.cls oficial e adaptado do acmart.cls (sigconf); este arquivo
% carrega o acmart e define como vazios os comandos extras do template.
% =====================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{webmedia}[2026/11/22 PROVISORIO: acmart + comandos do template WebMedia]
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{acmart}}
\ProcessOptions\relax
\LoadClass{acmart}
\ClassWarningNoLine{webmedia}{Usando webmedia.cls PROVISORIO. Substitua pelo oficial}
\newcommand{\setevent}[1]{}
\newcommand{\proceedingsDetails}[4][]{\acmConference[#1]{#2}{#3}{#4}\acmYear{#3}}
\def\ISSN#1{}
% sem o rodape ACM (ISBN/DOI ficticios) do acmart
\AtBeginDocument{\renewcommand\footnotetextcopyrightpermission[1]{}}
