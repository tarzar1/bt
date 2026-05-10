import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../constants.dart';
import '../providers/matrix_provider.dart';

class AnimationGrid extends ConsumerWidget {
  const AnimationGrid({super.key});

  static const _columns = 3;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final current = ref.watch(currentAnimProvider);
    final svc = ref.read(bleServiceProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.only(left: 4, bottom: 10),
          child: Text('Animaciones (25)',
              style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.bold,
                  color: Colors.white)),
        ),
        SizedBox(
          height: (animations.length / _columns).ceil() * 82.0,
          child: GridView.builder(
            physics: const NeverScrollableScrollPhysics(),
            padding: EdgeInsets.zero,
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: _columns,
              childAspectRatio: 2.6,
              crossAxisSpacing: 8,
              mainAxisSpacing: 8,
            ),
            itemCount: animations.length,
            itemBuilder: (context, i) {
              final a = animations[i];
              final active = current == a.name;
              return GestureDetector(
                onTap: () {
                  svc.anim(a.name);
                  ref.read(currentAnimProvider.notifier).state = a.name;
                },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: active
                          ? a.colors.map((c) => Color(c)).toList()
                          : [const Color(0xFF1A2A3A), const Color(0xFF0D1E30)],
                    ),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: active
                          ? Color(a.colors[0])
                          : const Color(0xFF2A3A4A),
                      width: active ? 2 : 1,
                    ),
                  ),
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(a.name,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight:
                                  active ? FontWeight.bold : FontWeight.normal,
                              color: active ? Colors.white : const Color(0xFF8A9AAA),
                            )),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
