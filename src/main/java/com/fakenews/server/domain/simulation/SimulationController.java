package com.fakenews.server.domain.simulation;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/simulations")
@RequiredArgsConstructor
public class SimulationController {
    private final SimulationRepository simulations;
    private final SimulationAccess access;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public SimulationResponse create(@Valid @RequestBody CreateRequest request, Authentication authentication) {
        return response(simulations.save(Simulation.create(access.userId(authentication.getName()), request.name())));
    }

    @GetMapping("/{simulationId}")
    public SimulationResponse read(@PathVariable Long simulationId, Authentication authentication) {
        return response(access.requireRead(simulationId, authentication.getName()));
    }

    private SimulationResponse response(Simulation simulation) {
        return new SimulationResponse(simulation.getId(), simulation.getName());
    }

    public record CreateRequest(@NotBlank @Size(max = 100) String name) {}
    public record SimulationResponse(Long simulationId, String name) {}
}
