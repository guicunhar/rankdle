import { HelpCircle, X } from "lucide-react";
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

export default function HowToPlay() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", onKey);
    const { overflow } = document.body.style;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = overflow;
    };
  }, [open]);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="ml-auto flex items-center gap-1.5 rounded-md border border-ink-800 px-2.5 py-1.5 text-xs font-semibold text-ink-300 transition hover:border-ink-700 hover:text-ink-100"
      >
        <HelpCircle size={14} strokeWidth={2.5} />
        Como jogar?
      </button>

      {open &&
        createPortal(
          <div
            className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/70 p-4 py-[8vh]"
            onClick={() => setOpen(false)}
          >
            <div
              role="dialog"
              aria-modal="true"
              aria-labelledby="how-to-play-title"
              className="w-full max-w-lg rounded-xl border border-ink-800 bg-ink-900 p-6 shadow-xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-start justify-between gap-4">
                <h2
                  id="how-to-play-title"
                  className="font-display text-xl font-bold text-ink-50"
                >
                  Como jogar
                </h2>
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  aria-label="Fechar"
                  className="-mr-1 -mt-1 rounded-md p-1 text-ink-400 transition hover:bg-ink-800 hover:text-ink-100"
                >
                  <X size={20} strokeWidth={2.5} />
                </button>
              </div>

              <p className="mt-3 text-sm text-ink-300">
                Todo dia tem um ranking novo sobre um tema, por exemplo, "Pessoas
                mais seguidas do Instagram".
              </p>

              <ol className="mt-4 flex flex-col gap-3 text-sm text-ink-200">
                <li>
                  <span className="font-bold text-accent-400">1.</span> O jogo
                  pergunta sempre a mesma coisa: qual item está numa certa posição
                  do ranking? (Ex.: "Qual é a 34ª posição?")
                </li>
                <li>
                  <span className="font-bold text-accent-400">2.</span> Digite na
                  busca e escolha um item como palpite. A busca só aceita itens que
                  fazem parte desse ranking, e você pode ver quais são as opções.
                </li>
                <li>
                  <span className="font-bold text-accent-400">3.</span> Ao{" "}
                  <strong className="text-ink-50">Conferir</strong>, você descobre:
                  <ul className="mt-1.5 flex flex-col gap-1 border-l border-ink-800 pl-4 text-ink-300">
                    <li>a) A posição real do item que você chutou;</li>
                    <li>
                      b) Uma dica de direção: se a resposta está mais acima ou mais
                      abaixo na lista;
                    </li>
                    <li>
                      c) A pontuação do palpite: começa em{" "}
                      <strong className="text-ink-50">100</strong> e perde 1 ponto
                      para cada posição de distância entre o seu chute e a posição
                      perguntada. Ex.: A pergunta é a 34ª e o seu item está na 30ª →
                      4 de diferença → <strong className="text-ink-50">96</strong>{" "}
                      pontos. Cravar a posição exata ={" "}
                      <strong className="text-ink-50">100 pontos</strong>.
                    </li>
                  </ul>
                </li>
                <li>
                  <span className="font-bold text-accent-400">4.</span> Você tem 5
                  tentativas.
                </li>
                <li>
                  <span className="font-bold text-accent-400">5.</span> Sua nota do
                  dia é o seu melhor palpite.
                </li>
              </ol>
            </div>
          </div>,
          document.body,
        )}
    </>
  );
}
