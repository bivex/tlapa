--------------------------- MODULE DistributedLog ---------------------------

EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS
  \* Узлы кластера
  Nodes,
  \* Таймауты (в шагах)
  ElectionTimeoutMin, ElectionTimeoutMax,
  \* Максимальный размер лога для упрощения
  MaxLogSize

ASSUME
  ElectionTimeoutMin \in Nat,
  ElectionTimeoutMax \in Nat,
  ElectionTimeoutMax > ElectionTimeoutMin,
  MaxLogSize \in Nat,
  \* Nodes непустое множество идентификаторов (например, "n1", "n2", ...)
  Nodes \subseteq [id -> STRING]

VARIABLES
  \* Состояние каждого узла
  node_state,
  \* Текущий лидер (если известен)
  current_leader,
  \* Логи на каждом узле (последовательность записей)
  logs,
  \* Индекс последней применённой записи (commit index)
  commit_index,
  \* Счётчик терминов (单调 increasing)
  current_term,
  \* Голосование: кто за кого проголосовал в текущем термине
  voted_for,
  \* Таймеры (оставшиеся шаги до истечения)
  timers,
  \* Сообщения в сети (unordered set)
  messages,
  \* Счётчик сообщений для уникальности
  msg_id

\* ==================== Типы и константы ====================

\* Запись лога: término и команда
LogEntry == [term: Nat, command: STRING]

\* Состояние узла
NodeState == {
  "follower",   \* обычный узел, голосует, следит за лидером
  "candidate",  \* ищет лидера
  "leader"      \* лидер, отправляет heartbeat и реплицирует
}

\* Типы сообщений
MessageType == {
  "RequestVote",     \* кандидат просит голос
  "RequestVoteReply", \* ответ на запрос голоса
  "AppendEntries",   \* leader отправляет запись (или heartbeat)
  "AppendEntriesReply" \* подтверждение репликации
}

\* Сообщение
Message == [
  type: MessageType,
  to: STRING,
  from: STRING,
  term: Nat,
  \* для RequestVote
  last_log_index: Nat,
  last_log_term: Nat,
  \* для AppendEntries
  prev_log_index: Nat,
  prev_log_term: Nat,
  entries: [Seq(LogEntry)],
  leader_commit: Nat,
  \* результат
  success: BOOLEAN,
  \* ID для уникальности
  msg_id: Nat
]

\* ==================== Вспомогательные функции ====================

\* Безопасный индекс для доступа к логу (вне границ -> None)
SafeLogAt(log, idx) ==
  IF idx \in DOMAIN log THEN log[idx] ELSE [term |-> 0, command |-> ""]

\* Последний индекс лога
LastLogIndex(log) == Len(log)

\* Последний термин лога
LastLogTerm(log) ==
  IF Len(log) = 0 THEN 0 ELSE log[Len(log)].term

\* Проверка "логи более свежие" для консенсуса
\* Узел A считается более свежим, если:
\*   - его последний термин больше, ИЛИ
\*   - термины равны, но длина лога больше
LogMoreUpToDate(log_a, log_b) ==
  LET term_a == LastLogTerm(log_a)
      term_b == LastLogTerm(log_b)
  IN term_a > term_b \/ (term_a = term_b /\ Len(log_a) > Len(log_b))

\* Проверка совпадения индекса и термина в логе
\* (используется в AppendEntries consistency check)
MatchEntry(log, index, term) ==
  index \in DOMAIN log /\ log[index].term = term

\* ==================== Инициализация ====================

\* Начальные значения
Init ==
  /\ node_state \in [Nodes -> NodeState]
  /\ current_leader \in [Nodes -> STRING]   \* может быть ""
  /\ logs \in [Nodes -> [0..MaxLogSize -> LogEntry]]
  /\ commit_index \in Nat
  /\ current_term \in Nat
  /\ voted_for \in [Nodes -> [Nodes -> BOOLEAN]]  \* voted_for[node][target] = TRUE если проголосовал
  /\ timers \in [Nodes -> Nat]
  /\ messages = {}
  /\ msg_id = 0

\* Также инициализируем:
\* - все узлы как followers
\* - пустые логи
\* - таймеры случайные (но для детерминизма можно фиксировать)
\* - commit_index = 0, current_term = 1

\* ==================== Движение времени ====================

\* Шаг времени (уменьшаем таймеры)
Tick ==
  /\ msg_id' = msg_id + 1
  /\ node_state' = node_state
  /\ current_leader' = current_leader
  /\ logs' = logs
  /\ commit_index' = commit_index
  /\ current_term' = current_term
  /\ voted_for' = voted_for
  /\ timers' = [n \in Nodes |
      IF timers[n] > 0 THEN timers[n] - 1 ELSE 0]
  /\ messages' = messages

\* ==================== Поведение узла ====================

\* Выбор лидера (фолловер истекает таймер)
\* - кандидат увеличивает term, сбрасывает таймер, просит голоса
ElectionTimeout(node) ==
  /\ node_state[node] = "follower"
  /\ timers[node] = 0
  /\ node_state' = [node_state EXCEPT ![node] = "candidate"]
  /\ current_term' = current_term + 1
  /\ voted_for' = [n \in Nodes |
      IF n = node THEN [n \in Nodes |-> TRUE] ELSE voted_for[n]]
  /\ timers' = [n \in Nodes |
      IF n = node THEN ElectionTimeoutMax ELSE timers[n]]
  /\ messages' = messages ∪ {
      [type |-> "RequestVote",
       to |-> n',
       from |-> node,
       term |-> current_term' ,
       last_log_index |-> LastLogIndex(logs[node]),
       last_log_term |-> LastLogTerm(logs[node]),
       msg_id |-> msg_id',
       success |-> FALSE]
      : n' \in Nodes, n' # node
    }

\* Кандидат получает большинство голосов -> становится лидером
BecomeLeader(node) ==
  /\ node_state[node] = "candidate"
  /\ current_term >= current_term \* (термин уже увеличен)
  /\ voted_for[node][node] = TRUE
  /\ \A n \in Nodes \ {node}: voted_for[n][node]          \* все проголосовали за него
  /\ CurrentMajority(Nodes, LAMBDA n: voted_for[n][node]) = TRUE
  /\ node_state' = [node_state EXCEPT ![node] = "leader"]
  /\ current_leader' = [current_leader EXCEPT ![node] = node]
  /\ timers' = [n \in Nodes | IF n = node THEN ElectionTimeoutMax ELSE timers[n]]
  /\ messages' = messages ∪ {
      [type |-> "AppendEntries",
       to |-> n',
       from |-> node,
       term |-> current_term,
       prev_log_index |-> LastLogIndex(logs[node]),
       prev_log_term |-> LastLogTerm(logs[node]),
       entries |-> <<>>,    \* empty heartbeat
       leader_commit |-> commit_index,
       msg_id |-> msg_id' + Index(n'),
       success |-> FALSE]
      : n' \in Nodes \ {node}
    } \* id увеличены

\* Фолловер переходит на новый срок ( salamander term)
StepDown(node, new_term) ==
  /\ node_state[node] \in {"follower", "candidate"}
  /\ new_term > current_term
  /\ node_state' = [node_state EXCEPT ![node] = "follower"]
  /\ current_leader' = [current_leader EXCEPT ![node] = ""]
  /\ current_term' = new_term
  /\ timers' = [n \in Nodes | IF n = node THEN ElectionTimeout min? ELSE timers[n]]
  /\ voted_for' = [voted_for EXCEPT ![node] = [n \in Nodes |-> FALSE]]
  /\ остальное без изменений

\* Обработка входящих сообщений ====================

\* RequestVote (RPC от кандидата)
HandleRequestVote(node, msg) ==
  /\ node_state[node] \in {"follower", "candidate"}
  /\ current_term >= msg.term   \* не устарело
  /\ LogMoreUpToDate(logs[node], logs?.at?[msg.last_log_index])  \* мой логи свежее
  /\ IF current_term = msg.term THEN voted_for[node][msg.from] = FALSE  \* уже проголосовал
      ELSE "don't care"
  /\ IF博会 не начислять больше одного голоса в одном термине
  \* (в упрощённой модели разрешаем переголосовать при смене термина)
  THEN \E new_vote: new_vote \in Nodes
  ELSE "skip"
  \* На практике: если current_term > msg.term -> отклоняем
  \* Если current_term = msg.term и я ещё не голосовал -> одобряем
  \* иначе отклоняем

\* Упрощённая более логичная обработка:
HandleRequestVote(node, msg) ==
  /\ node_state[node] \in {"follower", "candidate"}
  /\ current_term >= msg.term
  /\ IF current_term > msg.term THEN "reject"
     ELSE IF voted_for[node][msg.from] THEN "reject"
     ELSE IF LogMoreUpToDate(logs[node], [msg.last_log_index |-> LogEntry[term |-> msg.last_log_term]])
          THEN \* grant vote
            voted_for' = [voted_for EXCEPT ![node][msg.from] = TRUE]
            /\ messages' = messages ∪ {
                [type |-> "RequestVoteReply",
                 to |-> msg.from,
                 from |-> node,
                 term |-> current_term,
                 msg_id |-> msg_id' + Index(node),
                 success |-> TRUE]
              }
          ELSE "reject"
  /\ остальные переменные не меняются

\* AppendEntries (heartbeat или replicated log)
HandleAppendEntries(node, msg) ==
  /\ node_state[node] \in {"follower", "candidate"}
  /\ IF msg.term < current_term THEN "reject"  \* устаревшее
     ELSE  \* валидный термин или выше
       IF msg.term > current_term THEN
          \* перейти на новый term как follower
          node_state' = [node_state EXCEPT ![node] = "follower"]
       ELSE node_state' = node_state
       /\ current_term' = msg.term
       /\ current_leader' = [current_leader EXCEPT ![node] = msg.from]
       /\ timers' = [timers EXCEPT ![node] = ElectionTimeoutMax]  \* reset timer
       \* Проверка consistency лога: prev_log_index должен совпадать
       IF msg.prev_log_index = 0 \/ MatchEntry(logs[node], msg.prev_log_index, msg.prev_log_term) THEN
          \* Успешно: добавляем entries и обновляем commit_index
          LET new_entries == IF Len(msg.entries) > 0 THEN
                              [e \in msg.entries | e]  \* копируем
                            ELSE <<>>
          \* Объединяем старую часть (до prev_log_index) и новые записи
          new_log == [logs[node] |-> [i \in 1..msg.prev_log_index |-> logs[node][i]]]
                       \cup [i \in 1..Len(new_entries) |
                               msg.prev_log_index + i |-> new_entries[i]]
          \* Обрезаем до MaxLogSize
          logs' = [logs EXCEPT ![node] = [i \in 1..Min(MaxLogSize, Len(new_log)) |
                       |-> new_log[i]]]
          /\ commit_index' = Max(commit_index, msg.leader_commit)
          /\ answer_success = TRUE
       ELSE
          logs' = logs
          /\ commit_index' = commit_index
          /\ answer_success = FALSE
       /\ messages' = messages ∪ {
           [type |-> "AppendEntriesReply",
            to |-> msg.from,
            from |-> node,
            term |-> current_term',
            msg_id |-> msg_id' + Index(node),
            success |-> answer_success,
            match_index |-> IF answer_success THEN
                              LastLogIndex(logs'[node])
                            ELSE 0]
         }

\* Обработка AppendEntriesReply (лидер получил акк от follower)
HandleAppendEntriesReply(leader, msg) ==
  /\ node_state[leader] = "leader"
  /\ current_term = msg.term
  /\ IF msg.success THEN
        \* обновить commit_index на основе quorum
        \* (упрощённо: считаем, что если majority подтвердили индекс, то коммитим)
        \* Нужно подсчитать сколько узлов имеют лог до match_index
        \* В этой модели нужно вести статистику по каждому индексу
        commit_index' = Max(commit_index, Min(MaxLogSize, msg.match_index))
     ELSE
        \* В случае конфликта follower может попросить переслать
        \* или лидер снизит prev_log_index и попробует снова (упрощаем)
        commit_index' = commit_index
  /\ остальные переменные неизменны

\* Клиент отправляет команду (внешнее событие)
ClientSubmit(node, cmd) ==
  /\ node_state[node] = "leader"
  /\ msg_id' = msg_id + 1
  /\ current_term' = current_term
  /\ logs' = [logs EXCEPT ![node] = Append(logs[node],
        [term |-> current_term,
         command |-> cmd])]
  /\ сразу отправляем AppendEntries всем follower (асинхронно)
  /\ messages' = messages ∪ {
      [type |-> "AppendEntries",
       to |-> n,
       from |-> node,
       term |-> current_term,
       prev_log_index |-> LastLogIndex(logs[node]) - 1,
       prev_log_term |-> IF LastLogIndex(logs[node]) > 1
                           THEN logs[node][LastLogIndex(logs[node]) - 1].term
                           ELSE 0,
       entries |-> <<[term |-> current_term, command |-> cmd]>>,
       leader_commit |-> commit_index,
       msg_id |-> msg_id' + Index(n),
       success |-> FALSE]
      : n \in Nodes \ {node}
    }

\* Применение коммитованных записей (state machine)
\* Упрощённо: state machine = переменная, которая меняется при коммите
\* В реальности - нужно применять последовательно на каждом узле
ApplyCommitted ==
  \* каждый узел проверяет записи в своём логе до commit_index и применяет
  \* Упрощение: храним отдельно applied_index
  \* Но в нашей модели нет state, только логи. Можно добавить applied_index переменную.
  Skipped for brevity

\* ==================== Действия системы ====================

\* Все возможные действия в системе
Next ==
  \* 1) Tick (время идёт, таймеры)
  Tick
  \* 2) Элекция (любой узел может истечь и стать кандидатом)
  \/ \E n \in Nodes: ElectionTimeout(n)
  \* 3) Стать лидером (небольшой disabled - обычно это часть RequestVote)
  \/ \E n \in Nodes: BecomeLeader(n)
  \* 4) Принять сообщение RequestVote
  \/ \E n \in Nodes, m \in messages:
      m.type = "RequestVote" /\ m.to = n /\ HandleRequestVote(n, m)
  \* 5) Принять сообщение AppendEntries
  \/ \E n \in Nodes, m \in messages:
      m.type = "AppendEntries" /\ m.to = n /\ HandleAppendEntries(n, m)
  \/ \E n \in Nodes, m \in messages:
      m.type = "AppendEntriesReply" /\ m.to = n /\ HandleAppendEntriesReply(n, m)
  \* 6) Клиент отправляет команду лидеру
  \/ \E n \in Nodes, cmd \in STRING: ClientSubmit(n, cmd)
  \* 7) Удалить обработанные сообщения (после отправки ответов)
  \/ messages' = messages \ {m \in messages: m.type \in {"RequestVoteReply","AppendEntriesReply"}}
  \* остальные переменные без изменений

\* ==================== Инварианты и свойства ====================

\* LeaderAppendOnly: лидер не перезаписывает прошлые записи
LeaderAppendOnly ==
  \A n \in Nodes: node_state[n] = "leader" =>
    \A i \in 1..(LastLogIndex(logs[n]) - 1):
      logs[n][i] = logs[n]'[i]

\* LogsMatchCommonPrefix: если два узла имеют записи на одном индексе с одинаковым тер-
\* мином, то эти записи идентичны (индуктивно следует из AppendEntries)
LogsMatchCommonPrefix ==
  \A n1, n2 \in Nodes, i \in DOMAIN logs[n1] \cap DOMAIN logs[n2]:
    (logs[n1][i].term = logs[n2][i].term) => logs[n1][i] = logs[n2][i]

\* CommitOnlyIfQuorum: коммит происходит только если majority подтвердили
CommitOnlyIfQuorum ==
  \A idx > commit_index:
    \E quorum \subset Nodes:
      Card(quorum) > (Card(Nodes) \div 2) /\
      \A n \in quorum: idx \in DOMAIN logs[n] /\ logs[n][idx].term = current_term

\* Safety: только записи текущего термина лидера могут быть закоммичены
LeaderCompleteness ==
  \A n \in Nodes, idx \in 1..commit_index:
    \E l \in Nodes: node_state[l] = "leader" /\
      idx \in DOMAIN logs[l] /\ logs[l][idx].term = current_term

\* Liveness (частичная): если система устойчива, eventually лидер появится и начнёт реплицировать
EventualLeader ==
  \* Предполагаем, что сообщения доставляются и нет потерь узлов
  <> (\E n \in Nodes: node_state[n] = "leader")

\* ==================== Термины и определения ====================

THEOREM
  Safety ==
    \* Если запись закоммитена, то она останется на всех узлах и будет применена
    \* В этой модели: если commit_index >= i, то все живые узлы будут иметь эту запись
    LogsMatchCommonPrefix /\ CommitOnlyIfQuorum

THEOREM
  Liveness ==
    \* При стабильной сети (все сообщения доставляются) система прогрессирует
    \* Упрощённо: если клиент отправил команду лидеру, то она eventual commit
    \* не формализовано здесь из-за сложности

\* Некоторые вспомогательные теоремы для проверки
THEOREM
  TermMonotonicity ==
    \A n \in Nodes: node_state[n] \in {"follower", "candidate", "leader"} => current_term >= 1

THEOREM
  SingleLeader ==
    \A t1, t2 \in Nat:
      (\E n \in Nodes: node_state[n] = "leader" at t1) =>
      (\A m \in Nodes \ {n}: node_state[m] # "leader" at t1)

\* ==================== Трассировка для верификации ====================

\* Спецификация
Spec == Init /\ [][Next]_<<node_state, logs, commit_index, current_term, voted_for, timers, messages, msg_id>>

\* Инвариант типа (все значения в допустимых диапазонах)
TypeInvariant ==
  /\ node_state \in [Nodes -> NodeState]
  /\ logs \in [Nodes -> [0..MaxLogSize -> LogEntry]]
  /\ commit_index \in 0..MaxLogSize
  /\ current_term \in Nat
  /\ voted_for \in [Nodes -> [Nodes -> BOOLEAN]]
  /\ timers \in [Nodes -> 0..ElectionTimeoutMax]
  /\ messages \subset [type: MessageType, to: STRING, from: STRING, ...]
  /\ msg_id \in Nat

\*------------------ Текущая спецификация ------------------*
\* (для тестирования)

\* _________________________________________________________
\* E N D   O F   M O D U L E
\* ---------------------------------------------------------