#include <unistd.h>
#include <cassert>
#include <cstdio>
#include <algorithm>
#include <utility>
#include <vector>
#include "message.h"  // NOLINT
#include "virus.h"  // NOLINT

#define MAX_UNHEALTHY_NODES 3

// Overall solution strategy:
// The first problem to solve is that the infected nodes don't know they're
// infected. The way we solve this is that we divide the nodes in pairs, and the
// pairs exchange messages twice. This way each pair which contains two clean
// nodes will know it (and the pair as a whole will contain information needed
// to deduce which nodes in the pair were the source of infection, if any).
// The second problem is to get the information out of the infected pairs,
// without infecting the nodes that the information gets to. The way to solve
// this is "negative" information - that is, we will pass information by _not_
// sending a message. More precisely, for instance, if we want all the healthy
// pairs to report, we'll have all the healthy pairs send a message somewhere.
// Note that the receiver doesn't know how many messages they're to receive, so
// we have to implement a timeout. The way this works is that the even nodes
// will be the receivers (receiving via Receive(-1)), while the odd nodes will
// sleep for a time, and then send a "stop waiting" message to the even node.
//
// After that, the rest is implementation. We'll get the list of healthy nodes,
// and then out of each unhealthy pair get the information as to what was the
// source of the infection. The implementation here requires at least 8X + 2
// nodes, where X is the max unhealthy nodes (the calculation is - X unhealthy
// pairs, 3X listener pairs, and one master), a more efficient implementation is
// likely possible.

void Wait() {
  usleep(300000);
}

void Give(int target) {
  VirusPutChar(target, 1);
  VirusSend(target);
}

bool Get(int target) {
  VirusReceive(target);
  return GetChar(target);
}

int main() {
  // In general, we'll send single-char messages consisting of a one. If we ever
  // receive a zero, we're infected.
  int N = NumberOfNodes();
  int M = MyNodeId();

  assert(N % 2 == 0);
  int partner = M ^ 1;

  // Exchange messages with the partner. If the partner was an origin, we will
  // get an infected message (and we're now infected).
  Give(partner);
  bool partner_infected = !Get(partner);
  // Now, give back to the partner. This message will be infected if either we,
  // or the partner was infected.
  Give(partner);
  bool either_infected = !Get(partner);
  // Note that we can be in three states now: we can know that none of us was
  // the origin (both variables false), or that I am the origin and the partner
  // isn't (if the first variable is false and the second is true), or that the
  // partner is the origin, and my state is unknown (if the first message is
  // true, the second will be necessarily true in that case).
  // Also note that our current state with the partner is identical.

  // Now, there's a certain amount of setup needed; and it will be valid for
  // only certain nodes. Comments at each variable say for which nodes will it
  // be set up correctly.
  // List of all healthy even nodes. Valid on all even nodes.
  std::vector<int> healthy_even_nodes;
  // The complement of the list above. Valid on all even nodes.
  std::vector<int> unhealthy_even_nodes;
  // Node that will eventually print out the answer. Valid on all even nodes.
  int master = -1;
  // For each unhealthy node pair, the list of three nodes that will listen to
  // them. Valid on all even nodes.
  std::vector<int> listeners[MAX_UNHEALTHY_NODES];
  // Will be set (to the ID of the even unhealthy node listened to) on each node
  // listed in listeners. Otherwise, set to -1 (on all nodes).
  int listened = -1;
  // Is set (to the index of the listener in the listeners vector) on every
  // listener. Set to -1 on non-listeners.
  int listener_index = -1;
  // The listeners for a given unhealthy node pair. Valid on both elements
  // of the node pair, empty elsewhere.
  std::vector<int> my_listeners;

  // All the even healthy nodes signal all the even nodes.
  if ((M & 1) == 0 && !either_infected) {
    for (int i = 0; i < N; i += 2) {
      Give(i);
    }
  }

  // All the even nodes pick up signals in a loop. The odd nodes wait
  // (hopefully enough for all the signals to get in), and then send a stop
  // signal to the even nodes to break them out of the loop. This works
  // regardless of whether the receiving node is infected or not.
  if (M & 1) {
    Wait();
    Give(M ^ 1);
  } else {
    while (true) {
      int healthy = VirusReceive(-1);
      GetChar(healthy);
      if (healthy & 1) break;
      healthy_even_nodes.push_back(healthy);
    }
  }

  // We need to wait before sending any more messages. Otherwise, the messages
  // we send now might get mixed up with the messages reporting healthiness
  // above.
  Wait();
  Wait();

  if ((M & 1) == 0) {
    // The sort is needed here for determinism later on (where we designate the
    // master node, and listener nodes, based on the order in this array; and we
    // need all the even nodes to designate the same master and listeners).
    std::sort(healthy_even_nodes.begin(), healthy_even_nodes.end());
    // Look for each even node in the set of healthy nodes. If we don't find a
    // node, it must be a part of an unhealthy pair.
    for (int i = 0; i < N; i += 2) {
      if (std::find(healthy_even_nodes.begin(), healthy_even_nodes.end(), i) ==
          healthy_even_nodes.end()) {
        unhealthy_even_nodes.push_back(i);
      }
    }
    assert(unhealthy_even_nodes.size() <= MAX_UNHEALTHY_NODES);
    // We presume all the even nodes have the same set of healthy nodes. So,
    // let's designate some special nodes in there. First, we designate the
    // first healthy node as the overall master. Note that the unhealthy even
    // nodes are in the same position, they also know about all the healthy
    // nodes.
    master = healthy_even_nodes[0];
    // Then, for each unhealthy node pair, we designate three listeners.
    int curr = 1;
    for (int i = 0; i < unhealthy_even_nodes.size(); ++i) {
      for (int j = 0; j < 3; ++j) {
        listeners[i].push_back(healthy_even_nodes[curr]);
        // Make note if I'm a listener.
        if (healthy_even_nodes[curr] == (M & ~1)) {
          listened = unhealthy_even_nodes[i];
          listener_index = j;
        }
        curr += 1;
      }
    }
  }
  // Now, each unhealthy node pair needs to determine who was the
  // origin of the infection out of the pair. For this, both the even node
  // and the odd node need to send data (because the even node doesn't know it
  // all). So, the dedicated master will send the data to the odd unhealthy
  // nodes. For ease of coding, we'll also send it to the even nodes.
  // Note the comparison "M == master" works correctly on odd nodes, since
  // "master" is initialized to -1.
  if (M == master) {
    for (int i = 0; i < unhealthy_even_nodes.size(); ++i) {
      for (int j = 0; j < 3; ++j) {
        VirusPutChar(unhealthy_even_nodes[i] ^ 1, listeners[i][j]);
        VirusPutChar(unhealthy_even_nodes[i], listeners[i][j]);
      }
      VirusSend(unhealthy_even_nodes[i] ^ 1);
      VirusSend(unhealthy_even_nodes[i]);
    }
  }
  // In the meantime, the healthy odd nodes don't know whether they're
  // listeners, and their even counterparts should tell them.
  if (!either_infected) {
    if ((M & 1) == 0) {
      VirusPutChar(M ^ 1, listener_index + 1);
      VirusSend(M ^ 1);
    } else {
      VirusReceive(M ^ 1);
      listener_index = GetChar(M ^ 1) - 1;
      if (listener_index != -1) listened = 1;
    }
  }

  if (either_infected) {
    master = VirusReceive(-1);
    for (int i = 0; i < 3; ++i) my_listeners.push_back(GetChar(master));
    // Now, the infected nodes send data to the listeners. See below for
    // details.
    if (partner_infected) {
      Give(my_listeners[1 + (M & 1)]);
    } else {
      // I am infected, my partner isn't
      Give(my_listeners[0]);
    }
  }
  // There are three cases now:
  // * If they are both infected, the odd node sends a message to listener 2,
  //   the even node sends a message to listener 1, and listener 0 gets nothing.
  // * If only the odd node is infected, then the even node sends a message to
  //   listener 1, while the odd node sends messages to listener 0. Listener 2
  //   gets nothing.
  // * if only the even node is infected, then the odd node sends a message to
  //   listener 2, while the even node sends a message to listener 0. Listener 1
  //   gets nothing.
  if (listened != -1) {
    if (M & 1) {
      Wait();
      Give(M ^ 1);
    } else {
      int sender = VirusReceive(-1);
      if (sender == (M ^ 1)) {
        // Aha - we got a message from our odd node, meaning no message from the
        // infected node we're listening to. So, we're still healthy, and we
        // know a part of the infected nodes. Let's tell the master.
        if (listener_index == 0) {
          VirusPutChar(master, 2);
          VirusPutChar(master, listened);
          VirusPutChar(master, listened ^ 1);
        } else if (listener_index == 1) {
          VirusPutChar(master, 1);
          VirusPutChar(master, listened);
        } else {
          assert(listener_index == 2);
          VirusPutChar(master, 1);
          VirusPutChar(master, listened ^ 1);
        }
        VirusSend(master);
      }
    }
  }
  // And now the master needs to pick up those messages.
  if (M == master) {
    std::vector<int> infection_origins;
    for (int i = 0; i < unhealthy_even_nodes.size(); ++i) {
      int sender = VirusReceive(-1);
      int data_size = GetChar(sender);
      for (int j = 0; j < data_size; ++j) {
        infection_origins.push_back(GetChar(sender));
      }
    }
    std::sort(infection_origins.begin(), infection_origins.end());
    PrintNumber(infection_origins.size());
    for (int i = 0; i < infection_origins.size(); ++i) {
      PrintNumber(infection_origins[i]);
    }
  }
  return 0;
}
