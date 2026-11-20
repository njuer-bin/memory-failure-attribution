%% ecai.cls --- LOCAL STAND-IN for the ECAI proceedings style.
%%
%% The official ECAI author kit (ecai.cls + .bst + sample) is distributed by
%% the conference and IOS Press and is not bundled here. This file reproduces
%% the *geometry* the paper is budgeted against --- A4, 9 pt, two columns,
%% IOS-Press-like margins --- so the 7-page body + 1-page references limit can
%% be measured locally before the official class is available. When the ECAI
%% 2027 kit is released, drop the official ecai.cls/.bst into this folder and
%% recompile; the front matter below is isolated so only \title, \author and
%% the abstract block would need to be re-checked.
%%
%% Not for camera-ready use.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ecai}[2026/11/20 v0.1 local ECAI-geometry stand-in]

\LoadClass[a4paper,9pt,twocolumn]{extarticle}

\RequirePackage[a4paper,
  top=2.4cm, bottom=2.5cm, left=1.95cm, right=1.95cm,
  columnsep=0.65cm, headsep=0.5cm, footskip=1.0cm]{geometry}
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
\RequirePackage{times}
\RequirePackage{microtype}
\RequirePackage{graphicx}
\RequirePackage{booktabs}
\RequirePackage{amsmath}
\RequirePackage{amssymb}
\RequirePackage{xcolor}

% --- sectioning: compact, bold, run-in-friendly -------------------------
\RequirePackage{titlesec}
\titleformat{\section}{\normalfont\bfseries\large}{\thesection}{0.6em}{}
\titlespacing*{\section}{0pt}{1.0ex plus 0.4ex}{0.5ex}
\titleformat{\subsection}{\normalfont\bfseries\normalsize}{\thesubsection}{0.5em}{}
\titlespacing*{\subsection}{0pt}{0.8ex plus 0.3ex}{0.35ex}
\titleformat{\subsubsection}[runin]{\normalfont\bfseries\normalsize}{}{0pt}{}[.]
\titlespacing*{\subsubsection}{0pt}{0.6ex plus 0.2ex}{0.4em}

% --- title block ---------------------------------------------------------
\renewcommand{\maketitle}{%
  \twocolumn[%
    \begin{center}%
      {\LARGE\bfseries \@title\par}%
      \vspace{1.0em}%
      {\normalsize \@author\par}%
      \vspace{0.8em}%
    \end{center}%
  ]%
}

% --- abstract: indented, slightly smaller ---------------------------------
\renewenvironment{abstract}{%
  \begin{center}\bfseries Abstract\end{center}%
  \list{}{\leftmargin=1.0em \rightmargin=1.0em}%
  \item\relax\small\noindent\ignorespaces
}{%
  \endlist
}

% --- caption sizes -------------------------------------------------------
\RequirePackage[font=small,labelfont=bf,labelsep=period]{caption}

% --- references: numbered, compact --------------------------------------
\RequirePackage[numbers,sort&compress]{natbib}
\setlength{\bibsep}{0.2ex plus 0.1ex}
\renewcommand{\bibfont}{\small}

% --- floats: allow tighter placement ------------------------------------
\renewcommand{\topfraction}{0.92}
\renewcommand{\bottomfraction}{0.7}
\renewcommand{\textfraction}{0.06}
\renewcommand{\floatpagefraction}{0.8}
\setcounter{topnumber}{4}
\setcounter{totalnumber}{6}
